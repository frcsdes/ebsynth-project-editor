import struct

from dataclasses import dataclass, field
from pathlib import Path
from typing import BinaryIO


# Supposedly, the current version of the program
MAGIC_PROGRAM_VERSION = 'EBS05'

# Supposedly, the current version of the project file structure
MAGIC_PROJECT_VERSION = 'V02'

# Uninterpreted integer value that appears at the end of project files
MAGIC_FINAL_INTEGER = 704


@dataclass
class EbSynthInterval:
	""" Represents an EbSynth frames interval. """

	# Number of the keyframe
	key_frame: int = 1

	# `True` if the first frame is used, `False` otherwise
	first_frame_is_used: bool = False

	# `True` if the final frame is used, `False` otherwise
	final_frame_is_used: bool = False

	# Number of the first frame
	first_frame: int = 1

	# Number of the final frame
	final_frame: int = 1

	# Relative path to the synthesized frames
	output_path: str = r'out\[#####].png'


@dataclass
class EbSynthProject:
	""" Represents an EbSynth project. """

	# Supposedly, the current version of the program
	program_version: str = MAGIC_PROGRAM_VERSION

	# Supposedly, the current version of the project file structure
	project_version: str = MAGIC_PROJECT_VERSION

	# Number of frames per second used for the After Effects export
	frames_per_second: float = 30.0

	# Relative path to the keyframe images
	keys_path: str = r'keys\[#####].png'

	# Relative path to the video images
	video_path: str = r'video\[#####].png'

	# Relative path to the mask images
	mask_path: str = r'mask\[#####].png'

	# `True` if the mask is used, `False` if it is not used
	use_mask: bool = False

	# Weight of the keyframe images
	keys_weight: float = 1.0

	# Weight of the video images
	video_weight: float = 4.0

	# Weight of the mask images
	mask_weight: float = 1.0

	# Mapping parameter that encourages strokes to appear at the same location
	mapping: float = 10.0

	# De-flicker parameter that suppress testure flickering between frames
	de_flicker: float = 1.0

	# Diversity parameters that controls the visual richness of the style
	diversity: float = 3500.0

	# All image intervals that are synthesized
	intervals: list[EbSynthInterval] = field(
		default_factory=lambda: [EbSynthInterval()]
	)

	# Quality of the synthesis detail
	synthesis_detail: int = 2

	# `True` if GPU is used for the synthesis, `False` if it is not used
	use_gpu: bool = True

	# Uninterpreted integer value that appears at the end of project files
	magic_number: int = MAGIC_FINAL_INTEGER


def bytes_to_bool(buffer: BinaryIO) -> bool:
	return struct.unpack('<?', buffer.read(1))[0]


def bool_to_bytes(value: bool) -> bytes:
	return struct.pack('<?', value)


def bytes_to_int(buffer: BinaryIO) -> int:
	return struct.unpack('<i', buffer.read(4))[0]


def int_to_bytes(value: int) -> bytes:
	return struct.pack('<i', value)


def bytes_to_float(buffer: BinaryIO) -> float:
	return struct.unpack('<f', buffer.read(4))[0]


def float_to_bytes(value: float) -> bytes:
	return struct.pack('<f', value)


def bytes_to_constant_string(buffer: BinaryIO, reference: str) -> str:
	return buffer.read(len(reference) + 1)[:-1]


def constant_string_to_bytes(string: str) -> bytes:
	return string.encode(encoding='ascii') + b'\0'


def bytes_to_variable_string(buffer: BinaryIO) -> str:
	length = bytes_to_int(buffer)
	return buffer.read(length).decode('ascii')


def variable_string_to_bytes(string: str) -> bytes:
	return int_to_bytes(len(string)) + string.encode(encoding='ascii')


def bytes_to_interval(buffer: BinaryIO) -> EbSynthInterval:
	return EbSynthInterval(
		key_frame=bytes_to_int(buffer),
		first_frame_is_used=bytes_to_bool(buffer),
		final_frame_is_used=bytes_to_bool(buffer),
		first_frame=bytes_to_int(buffer),
		final_frame=bytes_to_int(buffer),
		output_path=bytes_to_variable_string(buffer),
	)


def interval_to_bytes(interval: EbSynthInterval) -> bytes:
	return bytes().join((
		int_to_bytes(interval.key_frame),
		bool_to_bytes(interval.first_frame_is_used),
		bool_to_bytes(interval.final_frame_is_used),
		int_to_bytes(interval.first_frame),
		int_to_bytes(interval.final_frame),
		variable_string_to_bytes(interval.output_path),
	))


def bytes_to_project(buffer: BinaryIO) -> EbSynthProject:
	return EbSynthProject(
		program_version=bytes_to_constant_string(buffer, MAGIC_PROGRAM_VERSION),
		video_path=bytes_to_variable_string(buffer),
		mask_path=bytes_to_variable_string(buffer),
		keys_path=bytes_to_variable_string(buffer),
		use_mask=bytes_to_bool(buffer),
		keys_weight=bytes_to_float(buffer),
		video_weight=bytes_to_float(buffer),
		mask_weight=bytes_to_float(buffer),
		mapping=bytes_to_float(buffer),
		de_flicker=bytes_to_float(buffer),
		diversity=bytes_to_float(buffer),
		intervals=[
			bytes_to_interval(buffer)
			for _ in range(bytes_to_int(buffer))
		],
		project_version=bytes_to_constant_string(buffer, MAGIC_PROJECT_VERSION),
		synthesis_detail=bytes_to_int(buffer),
		use_gpu=bytes_to_bool(buffer),
		frames_per_second=bytes_to_float(buffer),
		magic_number=bytes_to_int(buffer),
	)


def project_to_bytes(project: EbSynthProject) -> bytes:
	return bytes().join((
		constant_string_to_bytes(project.program_version),
		variable_string_to_bytes(project.video_path),
		variable_string_to_bytes(project.mask_path),
		variable_string_to_bytes(project.keys_path),
		bool_to_bytes(project.use_mask),
		float_to_bytes(project.keys_weight),
		float_to_bytes(project.video_weight),
		float_to_bytes(project.mask_weight),
		float_to_bytes(project.mapping),
		float_to_bytes(project.de_flicker),
		float_to_bytes(project.diversity),
		int_to_bytes(len(project.intervals)),
		*map(interval_to_bytes, project.intervals),
		constant_string_to_bytes(project.project_version),
		int_to_bytes(project.synthesis_detail),
		bool_to_bytes(project.use_gpu),
		float_to_bytes(project.frames_per_second),
		int_to_bytes(project.magic_number),
	))


def main():
	with open('test.ebs', 'wb') as file:
		file.write(project_to_bytes(EbSynthProject()))

	with open('test.ebs', 'rb') as file:
		print(bytes_to_project(file))


if __name__ == '__main__':
	main()
