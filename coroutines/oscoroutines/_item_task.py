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
from libopensesame.exceptions import osexception
from oscoroutines import injections
from oscoroutines._base_task import base_task

class item_task(base_task):

	"""
	desc:
		A task controls the coroutine for one item.
	"""

	def __init__(self, _item, start_time, end_time):

		"""
		desc:
			Constructor.

		arguments:
			item:
				desc:	An item object.
				type:	item
		"""

		if not hasattr(_item, u'coroutine'):
			print(u'inject coroutine into %s' % _item)
			try:
				_item.__class__.coroutine = getattr(injections, _item.item_type)
			except:
				raise osexception(
					u'%s not supported by coroutines' % _item.item_type)
		print(u'coroutine: %s' % _item.coroutine)
		self._item = _item
		base_task.__init__(self, start_time, end_time)

	def launch(self):

		"""See base_task."""

		self._item.prepare()
		self.coroutine = self._item.coroutine()
		print('launching %s' % self._item)
		self.coroutine.send(None)
