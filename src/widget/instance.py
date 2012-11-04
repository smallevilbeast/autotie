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

import os
import gtk


from accounts import AccountView

import utils

DATA_DIR = os.path.join(utils.get_parent_dir(__file__, 2), "data")

class TiebaWindow(gtk.Window):
    
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_size_request(600, 450)
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect("delete-event", gtk.main_quit)
        self.accounts_view = AccountView()
        
        self.__init_accounts()
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.add(self.accounts_view)
        self.add(scrolled_window)
        self.show_all()
        gtk.main()        
        
    def __init_accounts(self):    
        default_pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(os.path.join(DATA_DIR, "default_user.jpg"), 
                                                              32, 32)
        items = []
        items.append(({"icon" : default_pixbuf, "user_name" : "小邪兽", "passwd" : "123456", "status" : 0},))
        items.append(({"icon" : default_pixbuf, "user_name" : "小邪兽", "passwd" : "123456", "status" : 0},))
        items.append(({"icon" : default_pixbuf, "user_name" : "小邪兽", "passwd" : "123456", "status" : 0},))
        items.append(({"icon" : default_pixbuf, "user_name" : "小邪兽", "passwd" : "123456", "status" : 0},))
        items.append(({"icon" : default_pixbuf, "user_name" : "小邪兽", "passwd" : "123456", "status" : 0},))
        items.append(({"icon" : default_pixbuf, "user_name" : "小邪兽", "passwd" : "123456", "status" : 0},))
        items.append(({"icon" : default_pixbuf, "user_name" : "小邪兽", "passwd" : "123456", "status" : 0},))
        items.append(({"icon" : default_pixbuf, "user_name" : "小邪兽", "passwd" : "123456", "status" : 0},))
        self.accounts_view.set_items(items)
        
if __name__  == "__main__":        
    TiebaWindow()
        
    