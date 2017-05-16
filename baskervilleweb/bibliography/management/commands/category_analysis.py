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
    node_size=4
    node_label_distance=10
    padding=20
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
        self.context.set_font_size(12)
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

class Command(BaseCommand):
    args = 'outname'
    help = 'Create category graph'

    def handle(self, *args, **options):
        fname=args[0]
        
        cat_list=list(Category.objects.all())
        num_cats=len(cat_list)
        reverse={}
        for n in range(0,num_cats):
            reverse[cat_list[n].id]=n

        adjacency_matrix=numpy.zeros((num_cats,num_cats),dtype=numpy.int16)
        out_degree_matrix=numpy.zeros((num_cats,num_cats),dtype=numpy.int16)
        in_degree_matrix=numpy.zeros((num_cats,num_cats),dtype=numpy.int16)

        cat_rels=CategoryRelation.objects.all()
        L=len(cat_rels)

        next_perc=10
        n=0
        for rel in cat_rels:
            i=reverse[rel.father.id]
            j=reverse[rel.child.id]
            adjacency_matrix[(i,j)]=1
            out_degree_matrix[(i,i)]+=1
            in_degree_matrix[(j,j)]+=1
            n+=1
            if 100.0*float(n)/float(L) > next_perc:
                print("    %2.2f%%" % (100*float(n)/float(L)))
                next_perc+=10

        # outlaplace_matrix=outdegree_matrix-adjacency_matrix
        # inlaplace_matrix=indegree_matrix-adjacency_matrix

        # outeigenvalues,outaeigenvectors=numpy.linalg.eig(outlaplace_matrix)
        # ineigenvalues,inaeigenvectors=numpy.linalg.eig(inlaplace_matrix)


        # print "out",numpy.count_nonzero(outeigenvalues),num_cats
        # print "in",numpy.count_nonzero(ineigenvalues),num_cats

        out_laplace_matrix=out_degree_matrix-adjacency_matrix
        in_laplace_matrix=in_degree_matrix-adjacency_matrix

        out_eigenvalues,out_eigenvectors=numpy.linalg.eig(out_laplace_matrix)
        in_eigenvalues,in_eigenvectors=numpy.linalg.eig(in_laplace_matrix)

        print("out",numpy.count_nonzero(out_eigenvalues),num_cats)
        print("in",numpy.count_nonzero(in_eigenvalues),num_cats)

        print(CategoryTreeNode.objects.filter(level=0).count())

        ### draw

        k=20

        


        cg=CategoryGraph(fname,800,600)

        cg.draw_node(10,30,"nodo 1")
        cg.draw_node(100,30,"nodo 2")
        cg.draw_edge(10,30,100,30)
        
        cg.show_page()

