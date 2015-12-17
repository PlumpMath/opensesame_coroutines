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

def keyboard_response(self):

	"""
	desc:
		A coroutines() function to be injected into keyboard_response items.
	"""

	self._keyboard.timeout = 0
	alive = True
	yield
	self.set_item_onset()
	if self._flush:
		self._keyboard.flush()
	self.set_sri()
	while alive:
		key, time = self._keyboard.get_key()
		if key is not None:
			break
		alive = yield
	self.process_response_keypress((key, time))
	self.response_bookkeeping()

def sketchpad(self):

	"""
	desc:
		A coroutines() function to be injected into sketchpad items.
	"""

	yield
	self.set_item_onset(self.canvas.show())
