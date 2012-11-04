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

class BaseColumnTag(gtk.TreeViewColumn):
    
    def __init__(self, name):
        gtk.TreeViewColumn.__init__(self)
        label = gtk.Label(name)
        self.set_widget(label)
        label.show()
        
    def get_button(self):    
        return self.get_widget().get_ancestor(gtk.Button)
    
class AccountColumnTag(BaseColumnTag):        
    def __init__(self, name):
        BaseColumnTag.__init__(self, name)
        r = gtk.CellRendererText()
        r.set_property("xalign", 0)
        r.set_property("ellipsize", pango.ELLIPSIZE_END)
        self.pack_start(r, expand=True)
        self.add_attribute(r, "markup", 2)
        self.set_clickable(True)
    
    def get_button(self):
        return self.get_widget().get_ancestor(gtk.Button)

class AccountColumnPixbuf(BaseColumnTag):    
    def __init__(self, name):
        BaseColumnTag.__init__(self, "")
        r = gtk.CellRendererPixbuf()
        self.pack_start(r)
        self.add_attribute(r, "pixbuf", 4)
    

class UserView()


