#-*- coding:utf-8 -*-

"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""

from libopensesame.py3compat import *
import os
from PyQt4 import QtGui, QtCore
from libqtopensesame.items.sequence import sequence
from libqtopensesame.widgets.tree_item_item import tree_item_item
from libqtopensesame.validators import duration_validator
from libqtopensesame.misc import _
from oscoroutines import coroutines, items_adapter, tree_overview_adapter

class qtcoroutines(coroutines, sequence):

	def item_icon(self):

		"""See item."""

		if self.qicon is not None:
			return self.qicon
		plugin_folder = os.path.dirname(os.path.dirname(__file__))
		icon16 = os.path.join(
			plugin_folder, u'%s.png' % self.item_type)
		icon32 = os.path.join(
			plugin_folder, u'%s_large.png' % self.item_type)
		self.qicon = QtGui.QIcon()
		self.qicon.addFile(icon16, QtCore.QSize(16, 16))
		self.qicon.addFile(icon32, QtCore.QSize(32, 32))
		return self.qicon

	@property
	def items(self):

		"""
		desc:
			A property that maps the schedule list to an items list as expected
			by sequence.
		"""

		return self._items

	@items.setter
	def items(self, val):

		"""
		desc:
			A setter that maps an items list to a schedule list.
		"""

		for i, (item_name, cond) in enumerate(val):
			start_time = self.schedule[i][1]
			end_time = self.schedule[i][2]
			self.schedule[i] = item_name, start_time, end_time, cond

	def init_edit_widget(self):

		"""See qtitem."""

		super(sequence, self).init_edit_widget(False)
		self._items = items_adapter(self.schedule)
		self.treewidget = tree_overview_adapter(self, self.main_window,
			overview_mode=False)
		self.treewidget.setup(self.main_window)
		self.treewidget.structure_change.connect(self.update)
		self.treewidget.text_change.connect(self.update_script)
		self.treewidget.setHeaderLabels([_(u'Item name'), (u'Run if'),
			_(u'Start time'), _(u'End time')])
		self.set_focus_widget(self.treewidget)
		self.edit_vbox.addWidget(self.treewidget)
		self.add_text(u"This plug-in is a proof of concept. It's "
			u'functionality may change.')
		self.add_line_edit_control(u'duration', u'Duration',
			u'Total duration of the coroutines').setValidator(
			duration_validator(self.main_window, default=u'5000'))
		self.add_line_edit_control(u'function_name',
			u'Generator function name (optional)',
			u'The name of a Python generator function in an inline_script')
		self.add_checkbox_control(u'flush_keyboard',
			u'Flush pending key presses at coroutines start',
			u'Flush pending key presses at coroutines start')

	def build_item_tree(self, toplevel=None, items=[], max_depth=-1,
		extra_info=None):

		"""See qtitem."""

		widget = tree_item_item(self, extra_info=extra_info)
		items.append(self.name)
		if max_depth < 0 or max_depth > 1:
			for item, start_time, end_time, cond in self.schedule:
				if item in self.experiment.items:
					self.experiment.items[item].build_item_tree(widget, items,
						max_depth=max_depth-1, extra_info=cond)
					child = widget.child(widget.childCount()-1)
					child.setText(2, safe_decode(start_time))
					child.setText(3, safe_decode(end_time))
		if toplevel is not None:
			toplevel.addChild(widget)
		else:
			widget.set_draggable(False)
		return widget
