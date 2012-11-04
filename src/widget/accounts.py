#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2012 smallevilbeast
#
# Author:     smallevilbeast <houshao55@gmail.com>
# Maintainer: smallevilbeast <houshao55@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gtk

from collections import OrderedDict

class ColumnBase(gtk.TreeViewColumn):
    def __init__(self, tag, cell, title, width):
        super(ColumnBase, self).__init__(None, cell)
        
        self.tag = tag
        self.title = title
        if width < 10: width = 10
        
        self.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        self.set_fixed_width(width)
        self.set_resizable(True)
        self.set_clickable(True)
        self.set_max_width(400)
        self.set_min_width(10)
        label = gtk.Label(title)
        self.set_widget(label)
        label.show()
        
    def get_current_width(self):    
        if self.get_width() >= 10:
            return self.get_width()
        else:
            return self.get_fixed_width()
        
    def get_button(self):
        return self.get_widget().get_ancestor(gtk.Button)

    def set_font(self, new_font=None):
        pass
        
class TextColumn(ColumnBase):    
    def __init__(self, tag, title, width):
        self.cell = gtk.CellRendererText()
        self.set_font()
        
        super(TextColumn, self).__init__(tag, self.cell, title, width)
        self.set_cell_data_func(self.cell , self.__on_render_text)
        
    def set_font(self, new_font=None):
        self.cell.set_property("font", new_font) 

    def __on_render_text(self,column, cell, model, iter):
        item = model[iter][0]
        cell.set_property("text", item[self.tag])
        
class PixbufColumn(ColumnBase):        
    def __init__(self, tag, title, width):
        self.cell = gtk.CellRendererPixbuf()
        self.set_font()
        
        super(PixbufColumn, self).__init__(tag, self.cell, title, width)
        self.set_cell_data_func(self.cell , self.__on_render_pixbuf)
        
    def __on_render_pixbuf(self,column, cell, model, iter):
        item = model[iter][0]
        cell.set_property("pixbuf", item[self.tag])
        
    
class AccountView(gtk.TreeView):
    
    column_names = OrderedDict()
    column_names["icon"] = ""
    column_names["user_name"] = "帐号"
    column_names["passwd"] = "密码"
    column_names["status"] = "登陆状态"
    
    def __init__(self, *args):
        gtk.TreeView.__init__(self, *args)
        
        self.store_model = gtk.ListStore(object)
        
        for tag, title in self.column_names.items():
            if tag == "icon":
                self.append_column(PixbufColumn(tag, title, 32))
            else:    
                self.append_column(TextColumn(tag, title, 100))
            
        self.set_model(self.store_model)    
        
    def append_item(self, item):        
        self.store_model.append(item)
        
    def set_items(self, items):    
        self.store_model.clear()
        for item in items:
            self.store_model.append(item)
