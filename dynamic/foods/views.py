from django.shortcuts import render
from django.db.models import Sum
# Create your views here.

from django.views.generic import View,TemplateView,FormView,UpdateView,DetailView
from django.views.generic.dates import DayArchiveView,TodayArchiveView,WeekArchiveView
from django.contrib.auth.models import User
from django.utils.timezone import make_aware


from foods.models import FoodDiaryEntry,WeightDiaryEntry,MeasureUnit

from foods.forms import DiaryFormset

import datetime


def calories_balance(aggregate,base_total=None):
    if aggregate["fat__sum"]:
        fat_kcal=aggregate["fat__sum"]*9.3
    else:
        fat_kcal=0
    if aggregate["saturated_fat__sum"]:
        sat_kcal=aggregate["saturated_fat__sum"]*9.3
    else:
        sat_kcal=0
    if aggregate["protein__sum"]:
        pro_kcal=aggregate["protein__sum"]*4
    else:
        pro_kcal=0
    if aggregate["carbohydrate__sum"]:
        car_kcal=aggregate["carbohydrate__sum"]*3.8
    else:
        car_kcal=0
    if aggregate["sugar__sum"]:
        sug_kcal=aggregate["sugar__sum"]*3.8
    else:
        sug_kcal=0
    if aggregate["added_sugar__sum"]:
        asg_kcal=aggregate["added_sugar__sum"]*3.8
    else:
        asg_kcal=0
    if aggregate["alcohol__sum"]:
        alc_kcal=aggregate["alcohol__sum"]*7
    else:
        alc_kcal=0

    if not base_total:
        tot_kcal=fat_kcal+pro_kcal+car_kcal+alc_kcal
    else:
        tot_kcal=base_total
        
    if tot_kcal:
        return { "fat": 100*fat_kcal/tot_kcal, 
                 "protein": 100*pro_kcal/tot_kcal,
                 "saturated_fat": 100*sat_kcal/tot_kcal,
                 "sugar": 100*sug_kcal/tot_kcal,
                 "added_sugar": 100*asg_kcal/tot_kcal,
                 "alcohol": 100*alc_kcal/tot_kcal,
                 "sofas": 100*(asg_kcal+alc_kcal+sat_kcal)/tot_kcal,
                 "carbohydrate": 100*car_kcal/tot_kcal }
    return { "fat": 0,
             "saturated_fat": 0,
             "protein": 0,
             "sugar": 0,
             "added_sugar": 0,
             "alcohol": 0,
             "sofas": 0,
             "carbohydrate": 0 }

def diary_dated_pie(uid,date_list, object_list, extra_context):
    extra_context["userobj"]=User.objects.get(username=uid)
    extra_context["aggregates"] = object_list.aggregate(Sum("kcal"),
                                                        Sum("fat"),
                                                        Sum("carbohydrate"),
                                                        Sum("sugar"),
                                                        Sum("added_sugar"),
                                                        Sum("alcohol"),
                                                        Sum("protein"),
                                                        Sum("sodium"),
                                                        Sum("potassium"),
                                                        Sum("fiber"),
                                                        Sum("water"),
                                                        Sum("saturated_fat"))
    percs=calories_balance(extra_context["aggregates_simulation"])
    degree={}
    for k in percs.keys():
        degrees[k]=percs[k]*360/100.0
    extra_context["calories_degrees"]=degrees
    

def diary_dated_items(uid,date_list, object_list, extra_context):
    extra_context["userobj"]=User.objects.get(username=uid)
    extra_context["aggregates"] = object_list.filter(future=False).aggregate(Sum("kcal"),
                                                                             Sum("fat"),
                                                                             Sum("carbohydrate"),
                                                                             Sum("sugar"),
                                                                             Sum("added_sugar"),
                                                                             Sum("alcohol"),
                                                                             Sum("protein"),
                                                                             Sum("sodium"),
                                                                             Sum("potassium"),
                                                                             Sum("fiber"),
                                                                             Sum("water"),
                                                                             Sum("saturated_fat"))
    extra_context["aggregates_simulation"] = object_list.aggregate(Sum("kcal"),
                                                                   Sum("fat"),
                                                                   Sum("carbohydrate"),
                                                                   Sum("sugar"),
                                                                   Sum("added_sugar"),
                                                                   Sum("alcohol"),
                                                                   Sum("protein"),
                                                                   Sum("sodium"),
                                                                   Sum("potassium"),
                                                                   Sum("fiber"),
                                                                   Sum("water"),
                                                                   Sum("saturated_fat"))

    extra_context["aggregates_high_processed"]=object_list.filter(product__high_processed=True).aggregate(Sum("kcal"),
                                                                                                          Sum("fat"),
                                                                                                          Sum("carbohydrate"),
                                                                                                          Sum("sugar"),
                                                                                                          Sum("added_sugar"),
                                                                                                          Sum("alcohol"),
                                                                                                          Sum("protein"),
                                                                                                          Sum("sodium"),
                                                                                                          Sum("potassium"),
                                                                                                          Sum("fiber"),
                                                                                                          Sum("water"),
                                                                                                          Sum("saturated_fat"))

    if object_list:
        last=object_list.last()
        date_ref=datetime.datetime(last.time.year,last.time.month,last.time.day+1)
        extra_context["ref_weight"]=WeightDiaryEntry.objects.filter(user=extra_context["userobj"]).filter(time__lte=date_ref).last()
    else:
        extra_context["ref_weight"]=WeightDiaryEntry.objects.filter(user=extra_context["userobj"]).last()
        
    extra_context["calories_percentual"]=calories_balance(extra_context["aggregates"])
    extra_context["calories_percentual_simulation"]=calories_balance(extra_context["aggregates_simulation"])
    extra_context["calories_percentual_high_processed"]=calories_balance(extra_context["aggregates_high_processed"],
                                                                         base_total=extra_context["aggregates_simulation"]["kcal__sum"])

    extra_context["calories_reference"]= {
        "protein": { "min": 10, "max": 35 },
        "carbohydrate": { "min": 45, "max": 65 },
        "sugar": { "min": 0, "max": extra_context["calories_percentual_simulation"]["carbohydrate"]/3.0 },
        "fat": { "min": 25, "max": 35 },
        "saturated_fat": { "min": 0, "max": 10 },
        "sofas": { "min": 0, "max": 15 }, # sat. fat + added sugar + alcool
        }


    extra_context["salt_reference"]={
        "sodium": { "diseq":"&lt;","g":2.4 },
        "potassium": { "diseq":"&gt;","g":4.7 },
        }

    if extra_context["aggregates_simulation"]["kcal__sum"]:
        extra_context["salt_reference"]["fiber"]= { "diseq":"&gt;",
                                                    "g": max(14,14*extra_context["aggregates_simulation"]["kcal__sum"]/1000.0) }
    else:
        extra_context["salt_reference"]["fiber"]= { "diseq":"&gt;",
                                                    "g": 14 }
        

    micro={}
        
    for entry in object_list:
        for f_micro in entry.product.productmicronutrient_set.all():
            if not micro.has_key(f_micro.micro_nutrient.id):
                micro[f_micro.micro_nutrient.id]={
                    "micro_nutrient": f_micro.micro_nutrient,
                    "value": 0.0, 
                    "rda_perc": 0.0,
                    "value_simulation": 0.0,
                    "rda_perc_simulation": 0.0,
                    "details": [] }
            if not entry.future:
                micro[f_micro.micro_nutrient.id]["value"]+=f_micro.quantity*entry.quantity_real()/100.0
                if f_micro.micro_nutrient.rda > 0:
                    micro[f_micro.micro_nutrient.id]["rda_perc"]=100*micro[f_micro.micro_nutrient.id]["value"]/f_micro.micro_nutrient.rda
            micro[f_micro.micro_nutrient.id]["value_simulation"]+=f_micro.quantity*entry.quantity_real()/100.0
            micro[f_micro.micro_nutrient.id]["details"].append( (entry,(f_micro.quantity*entry.quantity_real()/100.0)) )
            if f_micro.micro_nutrient.rda > 0:
                micro[f_micro.micro_nutrient.id]["rda_perc_simulation"]=100*micro[f_micro.micro_nutrient.id]["value_simulation"]/f_micro.micro_nutrient.rda

            
    extra_context["micro_nutrients"]=micro.values()
        
    return date_list, object_list, extra_context

class DiaryDayArchiveView(DayArchiveView):
    model = FoodDiaryEntry
    date_field = "time"
    allow_empty = True

    def get_queryset(self):
        uid=self.kwargs["uid"]
        q=super(self.__class__,self).get_queryset()
        return q.filter(user__username=uid)

    def get_dated_items(self,*args,**kwargs):
        uid=self.kwargs["uid"]
        date_list, object_list, extra_context=super(self.__class__,self).get_dated_items(*args,**kwargs)
        return diary_dated_items(uid,date_list,object_list.order_by("time"),extra_context)

        
class DiaryTodayArchiveView(TodayArchiveView):
    model = FoodDiaryEntry
    date_field = "time"
    allow_empty = True

    def get_queryset(self):
        uid=self.kwargs["uid"]
        q=super(self.__class__,self).get_queryset()
        return q.filter(user__username=uid)

    def get_dated_items(self,*args,**kwargs):
        uid=self.kwargs["uid"]
        date_list, object_list, extra_context=super(self.__class__,self).get_dated_items(*args,**kwargs)
        return diary_dated_items(uid,date_list,object_list.order_by("time"),extra_context)
    

### reportlab library https://code.djangoproject.com/wiki/Charts
class DiaryTodayCaloriesPieView(TodayArchiveView):
    model = FoodDiaryEntry
    date_field = "time"
    allow_empty = True

    def get_queryset(self):
        uid=self.kwargs["uid"]
        q=super(self.__class__,self).get_queryset()
        return q.filter(user__username=uid)

    def get_dated_items(self,*args,**kwargs):
        uid=self.kwargs["uid"]
        date_list, object_list, extra_context=super(self.__class__,self).get_dated_items(*args,**kwargs)
        return diary_dated_pie(uid,date_list,object_list,extra_context)
    
class DiaryWeekArchiveView(WeekArchiveView):
    model = FoodDiaryEntry
    date_field = "time"
    week_format = "%W"
    allow_future = True

    def get_queryset(self):
        uid=self.kwargs["uid"]
        q=super(self.__class__,self).get_queryset()
        return q.filter(user__username=uid)

    def get_dated_items(self,*args,**kwargs):
        uid=self.kwargs["uid"]
        date_list, object_list, extra_context=super(self.__class__,self).get_dated_items(*args,**kwargs)
        date_list, object_list, extra_context = diary_dated_items(uid,date_list,object_list.order_by("time"),extra_context)
        
        aggregate_products={}
        date_dict={}

        for entry in object_list:
            if not date_dict.has_key( (entry.time.year,entry.time.month,entry.time.day) ):
                date_dict[(entry.time.year,entry.time.month,entry.time.day)]=entry.time
            if not aggregate_products.has_key(entry.product.id):
                aggregate_products[entry.product.id]={
                    "product": entry.product,
                    "quantity": 0,
                    "kcal": 0,
                    "fat": 0,
                    "saturated_fat": 0,
                    "carbohydrate": 0,
                    "sugar": 0,
                    "protein": 0,
                    "alcohol": 0,
                    "added_sugar": 0,
                    "salt": 0,
                    "sodium": 0,
                    "potassium": 0,
                    "fiber": 0,
                    "water": 0
                    }

            aggregate_products[entry.product.id]["quantity"]+=entry.quantity_real()
            aggregate_products[entry.product.id]["kcal"]+=entry.kcal
            aggregate_products[entry.product.id]["fat"]+=entry.fat
            aggregate_products[entry.product.id]["saturated_fat"]+=entry.saturated_fat
            aggregate_products[entry.product.id]["carbohydrate"]+=entry.carbohydrate
            aggregate_products[entry.product.id]["sugar"]+=entry.sugar
            aggregate_products[entry.product.id]["protein"]+=entry.protein
            aggregate_products[entry.product.id]["alcohol"]+=entry.alcohol
            aggregate_products[entry.product.id]["added_sugar"]+=entry.added_sugar
            aggregate_products[entry.product.id]["salt"]+=entry.salt
            aggregate_products[entry.product.id]["sodium"]+=entry.sodium
            aggregate_products[entry.product.id]["potassium"]+=entry.potassium
            aggregate_products[entry.product.id]["fiber"]+=entry.fiber
            aggregate_products[entry.product.id]["water"]+=entry.water

        date_list=date_dict.values()
        date_list.sort()
        extra_context["aggregate_products"]=aggregate_products.values()
        num_days=len(date_list)
        extra_context["num_days"]=num_days
        extra_context["first_day"]=date_list[0]
        extra_context["last_day"]=date_list[-1]
        
        old_ref_weight=extra_context["ref_weight"]
        extra_context["ref_weight"]={
            "base": old_ref_weight.base*num_days,
            "need": old_ref_weight.need*num_days,
            }

        extra_context["salt_reference"]["sodium"]["g"]*=num_days
        extra_context["salt_reference"]["potassium"]["g"]*=num_days

        return date_list, object_list, extra_context

class AddDiariesView(View):
    formset_class = DiaryFormset
    template_name = "foods/add_diaries.html"
    template_ok_name = "/foods/diaries_added.html"
    
    def get(self,request,*args,**kwargs):
        formset = self.formset_class()
        context = { "formset": formset }
        return render(request,self.template_name,context)

    def convert_date_time(self,cleaned_data):
        def parse_time(time_str,time_date):
            if time_str=="breakfast":
                return 7,15,0
            if time_str=="lunch":
                return 12,30,0
            if time_str=="dinner":
                return 19,30,00
            if time_str=="morning":
                return 10,30,00
            if time_str=="afternoon":
                return 16,30,00
            if time_str=="now":
                time_date=datetime.datetime.today()
            return time_date.hour,time_date.minute,time_date.second
    
        def parse_date(day_str,day_date):
            today=datetime.datetime.today()
            print day_str
            if day_str=="today":
                return today.year,today.month,today.day
            yesterday=today-datetime.timedelta(days=1)
            if day_str=="yesterday":
                return yesterday.year,yesterday.month,yesterday.day
            tomorrow=today+datetime.timedelta(days=1)
            if day_str=="tomorrow":
                return tomorrow.year,tomorrow.month,tomorrow.day
            return day_date.year,day_date.month,day_date.day

        time_str=cleaned_data["time"]
        day_str=cleaned_data["day"]
        time_date=cleaned_data["other_time"]
        day_date=cleaned_data["other_day"]

        year,month,day=parse_date(day_str,day_date)
        hour,minute,second=parse_time(time_str,time_date)
        return make_aware(datetime.datetime(year,month,day,hour,minute,second))

    def product_parse(self,cleaned_data): 
        return [ (cleaned_data["product"],cleaned_data["quantity"],cleaned_data["measure_unit"] ) ]

    def recipe_parse(self,cleaned_data): 
        measure=cleaned_data["measure_unit"]
        quantity=cleaned_data["quantity"]
        recipe=cleaned_data["recipe"]
        quantity_real=measure.factor*quantity
        totale_iniziale=recipe.total_weight
        totale_finale=recipe.final_weight
        portion_factor=quantity_real/float(totale_finale)
        g=MeasureUnit.objects.get(name="g")
        ret=[]
        for rp in recipe.recipeproduct_set.all():
            quota=portion_factor*rp.quantity_real()
            ret.append((rp.product,quota,g))
        return ret

    def frequent_parse(self,cleaned_data): 
        frequent=cleaned_data["frequent_diary_entry"]
        return [ (frequent.product,frequent.quantity,frequent.measure_unit) ]

    def post(self,request,*args,**kwargs):
        formset = self.formset_class(request.POST)
        if not formset.is_valid():
            context = { "formset": formset }
            return render(request,self.template_name,context)

        for form in formset:
            print form.cleaned_data
            user=form.cleaned_data["user"]
            d_time=self.convert_date_time(form.cleaned_data)
            entry_type=form.cleaned_data["entry_type"]
            if entry_type=="frequent":
                entry_list=self.frequent_parse(form.cleaned_data)
            elif entry_type=="recipe":
                entry_list=self.recipe_parse(form.cleaned_data)
            else:
                entry_list=self.product_parse(form.cleaned_data)
            for product,quantity,measure in entry_list:
                FoodDiaryEntry.objects.create(user=user,time=d_time,product=product,quantity=quantity,measure_unit=measure)
                print user,d_time,product,quantity,measure


        context = { "formset": self.formset_class() }
        return render(request,self.template_name,context)
        #return render(request,self.template_ok_name,context)
        
