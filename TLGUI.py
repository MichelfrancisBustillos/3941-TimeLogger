#!/usr/bin/python
# TLGUI.py

# TODO: add menu item to report member totals

import gtk
import pango
import Logger
import os
import re

class TL:
    
    def delete_event(self, w, ev, data=None):
        return False

    def destroy(self, w, data=None):    
        gtk.main_quit()

    def updateCombo(self, w, data=None):
        if not w.get_text() == "":
            #name = tuple(re.split(" ", w.get_text().lower()))
            #for n in self.tldb.names:
            #    if re.search("^" + name[0], n[0].lower()):
            #        self.cbox.set_active(self.tldb.names.index(n))
            #    elif len(name) == 2 and \
            #        re.search(name[1], n[0].lower()):
            #        self.cbox.set_active(self.tldb.names.index(n))
            name = w.get_text().lower()
            for n in self.tldb.names:
                if re.match(name, ' '.join(n).lower()):
                    self.cbox.set_active(self.tldb.names.index(n))
        else:
            self.cbox.set_active(-1)

    def button_clicked(self, w, data=None):
        name = self.tldb.names[self.cbox.get_active()]
        if self.cbox.get_active() != -1:
            lastaction = self.tldb.getLastAction(name[0], name[1])
            if lastaction == "in":
                self.tldb.log(name[0], name[1], "out")
            elif lastaction == "out":
                self.tldb.log(name[0], name[1], "in")
            else:
                self.tldb.log(name[0], name[1], "in")

            self.updateLogButton(self.cbox)

    def createCombo(self):
        self.cbox = gtk.combo_box_new_text()

        cbc = self.cbox.child
        cbc.modify_font(pango.FontDescription("38"))

        for name in self.tldb.names:
            self.cbox.append_text(name[0] + " " + name[1])

        self.cbox.connect("changed", self.updateLogButton)

        self.cbhbox = gtk.HBox()
        self.cbhbox.pack_start(gtk.Label(""))
        self.cbhbox.pack_start(self.cbox)
        self.cbhbox.pack_start(gtk.Label(""))

        self.mainvb.pack_start(self.cbhbox, False)

    def createLogButton(self):
        self.logb = gtk.Button()
        self.logblbl = gtk.Label("<span size='38000'>Log In</span>")
        self.logblbl.set_use_markup(True)
        self.logb.connect("clicked", self.button_clicked)
        self.logb.add(self.logblbl)
        self.lbhbox = gtk.HBox()
        self.lbhbox.pack_start(gtk.Label(""))
        self.lbhbox.pack_start(self.logb)
        self.lbhbox.pack_start(gtk.Label(""))
        self.mainvb.pack_start(self.lbhbox, False)

    def updateLogButton(self, cb, data=None):
        name = self.tldb.names[cb.get_active()]
        lastaction = self.tldb.getLastAction(name[0], name[1])
        if lastaction == "in":
            self.logblbl.set_text("<span size='38000'>Log Out</span>")
        elif lastaction == "out":
            self.logblbl.set_text("<span size='38000'>Log In</span>")
        else:
            self.logblbl.set_text("<span size='38000'>Log In</span>")
        self.logblbl.set_use_markup(True)

    def createMenu(self):
        self.menubar = gtk.MenuBar()
        self.mainvb.pack_start(self.menubar)

        self.adminmenu = gtk.Menu()
        self.adminitem = gtk.MenuItem("Admin")
        self.adminitem.set_submenu(self.adminmenu)
        self.addnewmemberitem = gtk.MenuItem("Add New Member")
        self.addnewmemberitem.connect("activate", self.getNewName)
        self.logoutallitem = gtk.MenuItem("Log Out All")
        self.logoutallitem.connect("activate", self.logOutAll)
        self.adminmenu.append(self.addnewmemberitem)
        self.adminmenu.append(self.logoutallitem)

        self.loggedinitem = gtk.MenuItem("List Logged In Members")
        self.loggedinitem.connect("activate", self.listloggedin)
        self.adminmenu.append(self.loggedinitem)

        self.menubar.append(self.adminitem)

    def logOutAll(self, w, data=None):
        self.tldb.logOutAll()
        message = gtk.MessageDialog(type=gtk.MESSAGE_INFO)
        message.set_markup("All users logged out.")
        self.updateLogButton(self.cbox)
        message.run()

    def getNewName(self, w, data=None):
        self.newmemberdialog = gtk.Dialog(title="Add New Member",
                                          flags=gtk.DIALOG_MODAL)
        label = gtk.Label("Type the new member's name:")
        self.newmemberdialog.vbox.pack_start(label, True, True, 0)

        hb = gtk.HBox()
        self.newmemberdialog.vbox.pack_start(hb, True, True, 0)

        self.te = gtk.Entry()
        hb.pack_start(self.te)

        b = gtk.Button("Add")
        b.connect("clicked", self.addNewMember)
        hb.pack_start(b)

        self.newmemberdialog.show_all()


    def addNewMember(self, w, nametext=None):
        # does not work, make sure split okay
        newname = tuple(re.split(" ", self.te.get_text()))
        if len(newname) >= 2:
            self.tldb.addNewMember(newname[0], newname[1])
        else:
            self.tldb.addNewMember(newname[0], " ")
            

        message = gtk.MessageDialog(type=gtk.MESSAGE_INFO)
        message.set_markup("New user added: " + \
                           newname[0] + " " + newname[1]) 
        self.newmemberdialog.destroy()
        message.run()
        
    def clearSearch(self, w, data=None):
        self.button_clicked(w, data)
        self.highlightText(self.searchEntry)

    def highlightText(self, w, ev=None, data=None):
        w.select_region(0, -1)

    def listloggedin(self, w, data=None):
        loggedin = self.tldb.getAllLoggedIn()

        self.loggedindialog = gtk.Dialog(title="Logged in Members", flags=gtk.DIALOG_MODAL)

        if len(loggedin) > 0:
            for name in loggedin:
                self.loggedindialog.vbox.pack_start(gtk.CheckButton(label=name[0] + " " + name[1]))
        else:
            self.loggedindialog.vbox.pack_start(gtk.Label("Nobody logged in."))

        self.loggedinbutton = gtk.Button("Okay")
        self.loggedinbutton.connect("clicked", lambda x: self.loggedindialog.destroy())
        self.loggedindialog.vbox.pack_start(self.loggedinbutton)
        self.loggedindialog.show_all()

    def __init__(self, tldb):
        self.tldb = tldb
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Team 3941 Time Logger")
        self.window.connect("delete_event", self.destroy)

        self.mainvb = gtk.VBox()
        self.window.add(self.mainvb)

        self.createMenu()

        self.mainvb.add(gtk.Label(""))

        self.searchhb = gtk.HBox(False, 0)

        self.mainvb.pack_start(self.searchhb, False)
        
        self.searchhb.pack_start(gtk.Label(""))
        self.label1 = gtk.Label("<span size='38000'>Search: </span>")
        self.label1.set_use_markup(True)
        self.searchhb.pack_start(self.label1, False, False, 0)

        self.searchEntry = gtk.Entry(max=0)
        self.searchEntry.connect("changed", self.updateCombo)
        self.searchEntry.connect("activate", self.clearSearch)
        self.searchEntry.connect("focus", self.highlightText)
        self.searchEntry.modify_font(pango.FontDescription("38"))
        self.searchhb.pack_start(self.searchEntry)
        self.searchhb.pack_start(gtk.Label(""))

        self.createCombo()
        self.createLogButton()

        self.mainvb.add(gtk.Label(""))

        self.window.show_all()

    def main(self):
        gtk.main()

if __name__ == "__main__":
    tldb = Logger.Logger()
    tl = TL(tldb)
    tl.main()
