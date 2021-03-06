#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys,numpy

import os.path

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from bibliography.models import Category,CategoryRelation,CategoryTreeNode

import cairo,math

class TextSizeCalculator(object):
    node_label_distance=5
    text_height=20

    def __init__(self):
        fname="/tmp/temp.svg"
        ps = cairo.SVGSurface(fname,300,300)
        self.context = cairo.Context(ps)
        self.context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL,
                                      cairo.FONT_WEIGHT_NORMAL)
        self.context.set_font_size(9)


    def __call__(self,text):
        (t_x, t_y, t_width, t_height, t_dx, t_dy) = self.context.text_extents(text)
        #return (t_width+2*self.node_label_distance,t_height+2*self.node_label_distance)
        return (t_width+2*self.node_label_distance,self.text_height)

text_size_calculator=TextSizeCalculator()        

class CategoryGraph(object):
    node_size=5
    node_label_distance=5
    text_height=20
    padding=40
    margin=20
    
    def __init__(self,fname,W,H):

        self.realW=W+2*self.padding+2*self.margin
        self.realH=H+2*self.padding+2*self.margin
        
        self.W=W
        self.H=H

        ps = cairo.SVGSurface(fname,self.realW,self.realH)

        self.context = cairo.Context(ps)

        ### background

        self.context.set_source_rgb(.9,.9,.9)
        self.context.rectangle(0, 0, self.realW, self.realH)
        self.context.fill()
        self.context.set_source_rgb(1,1,1)
        self.context.rectangle(self.margin, self.margin, self.realW-2*self.margin, self.realH-2*self.margin)
        self.context.fill()

        self.draw_grid(10,100)

        self.context.set_source_rgb(0, 0, 0)
        self.context.set_line_width(1)
        self.context.rectangle(self.margin, self.margin, self.realW-2*self.margin, self.realH-2*self.margin)
        self.context.stroke()

        ### plotting style
        self.context.set_source_rgb(0, 0, 0)
        self.context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL,
                                      cairo.FONT_WEIGHT_NORMAL)
        self.context.set_font_size(9)
        self.context.set_line_width(0.5)

    def draw_grid(self,little,big):
        self.context.set_source_rgb(0.5, 1, 1)
        x0=0
        x1=self.W
        y0=0
        y1=self.H
        self.context.set_line_width(0.1)
        for n in range(0,self.H+1,little):
            x,y=self.convert(x0,n)
            self.context.move_to(x,y)
            x,y=self.convert(x1,n)
            self.context.line_to(x,y)
            self.context.stroke()
        for n in range(0,self.W+1,little):
            x,y=self.convert(n,y0)
            self.context.move_to(x,y)
            x,y=self.convert(n,y1)
            self.context.line_to(x,y)
            self.context.stroke()
        self.context.set_line_width(0.3)
        for n in range(0,self.H+1,big):
            x,y=self.convert(x0,n)
            self.context.move_to(x,y)
            x,y=self.convert(x1,n)
            self.context.line_to(x,y)
            self.context.stroke()
        for n in range(0,self.W+1,big):
            x,y=self.convert(n,y0)
            self.context.move_to(x,y)
            x,y=self.convert(n,y1)
            self.context.line_to(x,y)
            self.context.stroke()
        
    def convert(self,x,y):
        return x+self.padding+self.margin,y+self.padding+self.margin

    def show_page(self):
        self.context.show_page()

    def draw_node(self,x,y,label):
        x,y=self.convert(x,y)
        (t_x, t_y, t_width, t_height, t_dx, t_dy) = self.context.text_extents(label)

        #self.context.move_to(x-t_width/2,y-self.node_label_distance)
        self.context.move_to(x+self.node_label_distance,y+(self.text_height-t_y)/2)
        self.context.show_text(label)
        #self.context.arc(x, y, self.node_size, 0, 2*math.pi)
        #self.context.fill()
        self.context.move_to(x,y)
        self.context.rel_line_to(t_width+2*self.node_label_distance,0)
        self.context.rel_line_to(0,self.text_height)
        self.context.rel_line_to(-t_width-2*self.node_label_distance,0)
        self.context.close_path()
        self.context.stroke()
    
    def draw_edge(self,x0,y0,x1,y1):
        x0,y0=self.convert(x0,y0)
        x1,y1=self.convert(x1,y1)
        self.context.move_to(x0,y0)
        self.context.line_to(x1,y1)
        self.context.stroke()

class Node(object):
    def __init__(self,cat):
        self.cat=cat
        self.x=0
        self.y=0

class Edge(object):
    def __init__(self,rel):
        self.father=rel.father
        self.child=rel.child
        self.from_node=None
        self.to_node=None

def calcolate_nodes(x_base,y_base,margin_x,margin_y,cat_node):
    children=CategoryTreeNode.objects.branch_nodes(cat_node,cat_node.level+1)
    root=Node(cat_node.content_object)
    root.x=x_base
    root.y=y_base

    t_width, t_height = text_size_calculator(cat_node.content_object.name)

    W_base=int(math.ceil(t_width+margin_x))
    H_base=int(math.ceil(t_height+margin_y))


    if not children:
        return (W_base,H_base,[root])
    nodes=[root]

    H=0
    W=W_base
    y=y_base
    x=x_base+W_base

    for child in children:
        (W_ch,H_ch,nodes_ch)=calcolate_nodes(x,y,margin_x,margin_y,child)
        W=max(W,W_base+W_ch)
        H+=H_ch
        y+=H_ch
        nodes+=nodes_ch

    return (W,H,nodes) 

class Command(BaseCommand):
    args = 'outname'
    help = 'Create category graph'

    def handle(self, *args, **options):
        fprefix=args[0]
        baseprefix=os.path.basename(fprefix)

        K=50

        roots=CategoryTreeNode.objects.roots()

        R={}

        html="<html><head></head><body>\n"

        W_base=120
        H_base=20

        for cat_node in roots:
            fname=fprefix+"_"+cat_node.node_id+'.svg'
            html+="<h1>"+cat_node.content_object.name+"</h1>\n"
            html+='<img src="./'+baseprefix+"_"+cat_node.node_id+'.svg"/>\n'

            nodes=[]
            edges=[]

            ### calcolo nodi/edge

            (W,H,nodes)=calcolate_nodes(0,0,10,5,cat_node)

            print(W,H,fname)

            ### svg plot
            cg=CategoryGraph(fname,W,H)

            for node in nodes:
                cg.draw_node(node.x,node.y,node.cat.name)

            for edge in edges:
                cg.draw_edge(edge.from_node.x,edge.from_node.y,
                             edge.to_node.x,edge.to_node.y)
        
            cg.show_page()

        html+="</body></html>\n"

        fd=open(fprefix+".html","w")
        fd.write(html)
        fd.close()
