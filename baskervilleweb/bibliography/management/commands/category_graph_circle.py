#! /usr/bin/python
# -*- coding: utf-8 -*-

import re,time,datetime,sys,numpy

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import django.core.files
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from bibliography.models import Category,CategoryRelation,CategoryTreeNode

import cairo,math

class CategoryGraph(object):
    node_size=2
    node_label_distance=5
    padding=40
    margin=20
    
    def __init__(self,fname,H,W):

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

        self.context.move_to(x-t_width/2,y-self.node_label_distance)
        self.context.show_text(label)
        self.context.arc(x, y, self.node_size, 0, 2*math.pi)
        self.context.fill()
    
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

class Command(BaseCommand):
    args = 'outname'
    help = 'Create category graph'

    def handle(self, *args, **options):
        fprefix=args[0]

        K=50

        roots=CategoryTreeNode.objects.roots()

        R={}

        html="<html><head></head><body>\n"

        for cat_node in roots:
            num_level=cat_node.branch_depth()
            Q=[0 for x in range(0,num_level)]
            print(cat_node)
            Q[0]=cat_node.branch_level_size(1)

            for level in range(1,len(Q)):
                cat_nodes=CategoryTreeNode.objects.branch_nodes(cat_node,level)
                for cat_leaf in cat_nodes:
                    Q[level]=max(Q[level],cat_leaf.branch_level_size(level+1))
            print("    Q",Q)
            RQ=[0 for x in range(0,num_level+1)]

            RQ[num_level]=0
            RQ[num_level-1]=K
            
            i=num_level-2
            while i>=0:
                RQ[i]=RQ[i+1]*( 1 + 1/( 2*math.sin(math.pi/(Q[i]+1)) ) )
                i-=1
                
            print("    R",RQ)
            R[cat_node.label]=RQ
            html+="<h1>"+cat_node.content_object.name+"</h1>\n"
            html+='<img src="./'+cat_node.label+'.svg"/>\n'

        return

        nodes=list(map(Node,list(Category.objects.all())))
        N=len(nodes)
        reverse={}
        for n in range(0,N):
            reverse[nodes[n].cat.id]=n

        edges=list(map(Edge,list(CategoryRelation.objects.all())))
        M=len(edges)

        for edge in edges:
            edge.from_node=nodes[reverse[edge.father.id]]
            edge.to_node=nodes[reverse[edge.child.id]]

        ### draw

        K=50

        w=round(math.sqrt(N))
        h=math.ceil(N/w)

        w=int(w)
        h=int(h)

        W=int((w-1)*K)
        H=int((h-1)*K)

        cg=CategoryGraph(fname,W,H)
        
        for x in range(0,int(w)):
            for y in range(0,int(h)):
                if x*w+y>=N: break
                print(x*w+y,"/",N,x,y)
                nodes[x*w+y].x=x*K
                nodes[x*w+y].y=y*K

        n=0
        for node in nodes:
            cg.draw_node(node.x,node.y,node.cat.label+" "+str(n))
            n+=1

        for edge in edges:
            cg.draw_edge(edge.from_node.x,edge.from_node.y,
                         edge.to_node.x,edge.to_node.y)
        
        cg.show_page()

