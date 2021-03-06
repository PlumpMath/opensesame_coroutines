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
from libopensesame.item import item
from oscoroutines import item_task, inline_task, injections

class coroutines(item):

	"""
	desc:
		The coroutines plugin runtime.
	"""

	description = u'Run items simultaneously'

	def reset(self):

		"""See item."""

		self.var.duration = 5000
		self.var.flush_keyboard = u'yes'
		self.var.function_name = u''
		self.schedule = []

	def is_coroutine(self, item_name):

		"""
		arguments:
			item_name:
				desc:	The name of an item.
				type:	str

		returns:
			desc:	True if the item is a coroutine, False otherwise.
			type:	bool
		"""

		_item = self.experiment.items[item_name]
		return hasattr(_item, u'coroutines') or \
			hasattr(injections, _item.item_type)

	def is_oneshot_coroutine(self, item_name):

		"""
		arguments:
			item_name:
				desc:	The name of an item.
				type:	str

		returns:
			desc:	True if the item is a one-shot coroutine, False otherwise.
			type:	bool
		"""

		_item = self.experiment.items[item_name]
		if hasattr(_item, u'is_oneshot_coroutine'):
			return _item.is_oneshot_coroutine
		return _item.item_type in injections.oneshot_coroutines

	def from_string(self, string):

		"""See item."""

		self.variables = {}
		self.comments = []
		self.reset()
		if string is None:
			return
		for s in string.split(u'\n'):
			self.parse_variable(s)
			# run item_name start=1000 end=2000 runif="always"
			cmd, arglist, kwdict = self.syntax.parse_cmd(s)
			if cmd != u'run' or not len(arglist):
				continue
			item_name = arglist[0]
			start_time = kwdict.get(u'start', 0)
			end_time = kwdict.get(u'end', 0)
			cond = kwdict.get(u'runif', u'always')
			self.schedule.append((item_name, start_time, end_time, cond))

	def to_string(self):

		"""See item."""

		s = item.to_string(self)
		for item_name, start_time, end_time, cond in self.schedule:
			if self.is_oneshot_coroutine(item_name):
				end_time = start_time
			s += u'\t' + self.syntax.create_cmd(u'run', [item_name], {
				u'start' : start_time,
				u'end' : end_time,
				u'runif' : cond
				}) + u'\n'
		return s

	def prepare(self):

		"""See item."""

		item.prepare(self)
		self._schedule = []
		for item_name, start_time, end_time, cond in self.schedule:
			if not self.python_workspace._eval(self.syntax.compile_cond(cond)):
				continue
			t = item_task(self.experiment.items[item_name],
				self.syntax.auto_type(self.syntax.eval_text(start_time)),
				self.syntax.auto_type(self.syntax.eval_text(end_time))
				)
			self._schedule.append(t)
		if self.var.function_name != u"":
			t = inline_task(self.var.function_name, self.python_workspace,
				0, self.var.duration)
			self._schedule.append(t)

	def run(self):

		"""See item."""

		self._schedule.sort(key=lambda task: task.start_time)
		# Launch all coroutines
		for task in self._schedule:
			task.launch()
		dt = 0
		active = []
		t0 = self.clock.time()
		i = 0
		while dt < self.var.duration:
			# Activate coroutines by start time
			while self._schedule and self._schedule[0].started(dt):
				active.append(self._schedule.pop(0))
				active.sort(key=lambda task: task.end_time)
			# Run all active coroutines
			active = [task for task in active if task.step()]
			# De-activate coroutines by end time
			while active and active[0].stopped(dt):
				active.pop(0)
			dt = self.clock.time()-t0
			i += 1
		print('killing after %d ms' % (self.clock.time()-t0))
		# Kill pending coroutines
		for task in active:
			task.kill()
		print('trampoline took %d ms' % (self.clock.time()-t0))
		self.experiment.var.coroutines_cycles = i
		self.experiment.var.coroutines_duration = dt
		self.experiment.var.coroutines_mean_cycle_duration = 1.*dt/i

	def var_info(self):

		"""See item."""

		l = []
		l.append( (u"coroutines_cycles", u"[Determined at runtime]") )
		l.append( (u"coroutines_duration", u"[Determined at runtime]") )
		l.append( (u"coroutines_mean_cycle_duration", u"[Determined at runtime]") )
		return l
