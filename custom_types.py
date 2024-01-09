"""
Adds custom types from dataclasses or namedtuples to the project.
"""
from collections import namedtuple


# The type used to define a command
CommandType = namedtuple("CommandType", [
	"command",
	"name",
	"hidden"
])

# The type used to define an editor option
OptionType = namedtuple("OptionType", [
	"name",
	"current_state",
	"callback_trigger"
])
