import argparse
import struct

from dataclasses import dataclass, field
from pathlib import Path
from typing import BinaryIO, Iterable, Sequence


# Supposedly, the current version of the program
MAGIC_PROGRAM_VERSION = 'EBS05'

# Supposedly, a string that indicates that the project has extra metadata
MAGIC_EXTRA_METADATA = 'V02'

# Uninterpreted value that appears at the end of projects with extra metadata
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

	# Number of frames per second
	frames_per_second: float = 30.0

	# Relative path to the keyframe images
	key_images_path: str = r'keys\[#####].png'

	# Relative path to the video images
	video_images_path: str = r'video\[#####].png'

	# Relative path to the mask images
	mask_images_path: str = r'mask\[#####].png'

	# `True` if the mask images are enabled, `False` otherwise
	mask_images_enabled: bool = False

	# Weight of the keyframe images
	key_images_weight: float = 1.0

	# Weight of the video images
	video_images_weight: float = 4.0

	# Weight of the mask images
	mask_images_weight: float = 1.0

	# Mapping parameter that encourages strokes to appear at the same location
	mapping: float = 10.0

	# De-flicker parameter that suppress testure flickering between frames
	de_flicker: float = 1.0

	# Diversity parameters that controls the visual richness of the style
	diversity: float = 3500.0

	# All frame intervals that are synthesized
	intervals: list[EbSynthInterval] = field(default_factory=list)

	# Quality of the synthesis detail
	synthesis_detail: int = 2

	# `True` if GPU is used for the synthesis, `False` otherwise
	use_gpu: bool = True


def get_synthesis_detail_name(level: int) -> str:
	""" Return the name of the given synthesis detail `level`. """

	match level:
		case 1:
			return 'High'
		case 2:
			return 'Medium'
		case 3:
			return 'Low'
		case 4:
			return 'Garbage'
		case _:
			return 'Unknown'


def print_interval(interval: EbSynthInterval, padding: int):
	""" Print formatted information about the given frames `interval`. """

	def is_used_symbol(value: bool) -> str:
		return 'Y' if value else 'N'

	print(
		f'{interval.first_frame:>{padding}}',
		is_used_symbol(interval.first_frame_is_used), '|',
		f'{interval.key_frame:>{padding}}', '|',
		f'{interval.final_frame:>{padding}}',
		is_used_symbol(interval.final_frame_is_used), '|',
		interval.output_path,
	)


def print_project(project: EbSynthProject):
	""" Print formatted information about the given `project`. """

	# Format the synthesis detail
	synthesis_detail_name = get_synthesis_detail_name(project.synthesis_detail)
	synthesis_detail = f'{project.synthesis_detail} ({synthesis_detail_name})'

	# All printed categories that contain field names and their value
	categories = {
		'Project': {
			'EbSynth version': project.program_version,
			'Frames per second': project.frames_per_second,
		},
		'Image paths': {
			'Key images path': project.key_images_path,
			'Video images path': project.video_images_path,
			'Mask images path': project.mask_images_path,
		},
		'Image weights': {
			'Key images weight': project.key_images_weight,
			'Video images weight': project.video_images_weight,
			'Mask images weight': project.mask_images_weight,
			'Mask images enabled': project.mask_images_enabled,
		},
		'Advanced': {
			'Mapping': project.mapping,
			'De-flicker': project.de_flicker,
			'Diversity': project.diversity,
		},
		'Performance': {
			'Synthesis detail': synthesis_detail,
			'Use GPU': project.use_gpu,
		}
	}

	# Print all information about the project
	for category_name, field_name_and_value in categories.items():
		print(category_name)
		print('-' * len(category_name))

		padding = max(map(lambda x: len(x[0]), field_name_and_value.items()))
		for name, value in field_name_and_value.items():
			print(f'{name}:'.ljust(padding + 1), value)

		print()

	# Print all intervals in the project
	intervals_label = 'Intervals'
	print('Intervals')
	print('-' * len(intervals_label))
	print(
		'Start   ', '?', '|',
		'Key     ', '|',
		'Final   ', '?', '|',
		'Output',
	)

	for interval in project.intervals:
		print_interval(interval, 8)


def read_bool(buffer: BinaryIO) -> bool:
	return struct.unpack('<?', buffer.read(1))[0]


def write_bool(buffer: BinaryIO, value: bool):
	return buffer.write(struct.pack('<?', value))


def read_int(buffer: BinaryIO) -> int:
	return struct.unpack('<i', buffer.read(4))[0]


def write_int(buffer: BinaryIO, value: int):
	return buffer.write(struct.pack('<i', value))


def read_float(buffer: BinaryIO) -> float:
	return struct.unpack('<f', buffer.read(4))[0]


def write_float(buffer: BinaryIO, value: float):
	return buffer.write(struct.pack('<f', value))


def read_constant_string(buffer: BinaryIO, reference: str) -> str:
	return buffer.read(len(reference) + 1)[:-1].decode('ascii')


def write_constant_string(buffer: BinaryIO, string: str):
	return buffer.write(string.encode(encoding='ascii') + b'\0')


def read_variable_string(buffer: BinaryIO) -> str:
	length = read_int(buffer)
	return buffer.read(length).decode('ascii')


def write_variable_string(buffer: BinaryIO, string: str):
	write_int(buffer, len(string))
	buffer.write(string.encode(encoding='ascii'))


def read_interval(buffer: BinaryIO) -> EbSynthInterval:
	""" Return a frames interval read from the given `binary buffer`. """

	return EbSynthInterval(
		key_frame=read_int(buffer),
		first_frame_is_used=read_bool(buffer),
		final_frame_is_used=read_bool(buffer),
		first_frame=read_int(buffer),
		final_frame=read_int(buffer),
		output_path=read_variable_string(buffer),
	)


def write_interval(buffer: BinaryIO, interval: EbSynthInterval):
	""" Write the given frames `interval` to the binary `buffer`. """

	write_int(buffer, interval.key_frame)
	write_bool(buffer, interval.first_frame_is_used)
	write_bool(buffer, interval.final_frame_is_used)
	write_int(buffer, interval.first_frame)
	write_int(buffer, interval.final_frame)
	write_variable_string(buffer, interval.output_path)


def read_project(buffer: BinaryIO) -> EbSynthProject:
	""" Return a project read from the given binary `buffer`. """

	# Construct the project from data that is always present
	project = EbSynthProject(
		program_version=read_constant_string(buffer, MAGIC_PROGRAM_VERSION),
		video_images_path=read_variable_string(buffer),
		mask_images_path=read_variable_string(buffer),
		key_images_path=read_variable_string(buffer),
		mask_images_enabled=read_bool(buffer),
		key_images_weight=read_float(buffer),
		video_images_weight=read_float(buffer),
		mask_images_weight=read_float(buffer),
		mapping=read_float(buffer),
		de_flicker=read_float(buffer),
		diversity=read_float(buffer),
		intervals=[read_interval(buffer) for _ in range(read_int(buffer))],
	)

	# Continue reading from the buffer if it has extra metadata
	if read_constant_string(buffer, MAGIC_EXTRA_METADATA):
		project.synthesis_detail = read_int(buffer)
		project.use_gpu = read_bool(buffer)
		project.frames_per_second = read_float(buffer)

	return project


def write_project(buffer: BinaryIO, project: EbSynthProject):
	""" Write the given `project` to the binary `buffer`. """

	write_constant_string(buffer, project.program_version)
	write_variable_string(buffer, project.video_images_path)
	write_variable_string(buffer, project.mask_images_path)
	write_variable_string(buffer, project.key_images_path)
	write_bool(buffer, project.mask_images_enabled)
	write_float(buffer, project.key_images_weight)
	write_float(buffer, project.video_images_weight)
	write_float(buffer, project.mask_images_weight)
	write_float(buffer, project.mapping)
	write_float(buffer, project.de_flicker)
	write_float(buffer, project.diversity)

	write_int(buffer, len(project.intervals))
	for interval in project.intervals:
		write_interval(buffer, interval)

	write_constant_string(buffer, MAGIC_EXTRA_METADATA)
	write_int(buffer, project.synthesis_detail)
	write_bool(buffer, project.use_gpu)
	write_float(buffer, project.frames_per_second)
	write_int(buffer, MAGIC_FINAL_INTEGER)


def read_project_or_return_default(path: Path | None) -> EbSynthProject:
	""" Return the project read from `path`, or a default if path is `None`. """

	if path is None:
		return EbSynthProject()
	else:
		with open(path, 'rb') as file:
			return read_project(file)


def write_project_or_print_it(path: Path | None, project: EbSynthProject):
	""" Write the `project` to `path`, or print it if path is `None`. """

	if path is None:
		print_project(project)
	else:
		with open(path, 'wb') as file:
			write_project(file, project)


def create_intervals(
	first: int,
	final: int,
	step: int,
	left: int,
	right: int,
	output: str,
) -> Iterable[EbSynthInterval]:
	"""
	Return frame intervals inside the `first` and `final` frame numbers,
	inclusive. Their keyframes are separated by `step` frames, and each
	interval contains `left + right + 1` frames. `output` is a format string
	that can be interpolated with placeholder `i` as an integer.
	"""

	def create_one_interval(index_and_key: tuple[int, int]) -> EbSynthInterval:
		""" Return a new interval around the given key frame. """

		index, interval_key_frame = index_and_key
		interval_first_frame = interval_key_frame - left
		interval_final_frame = min(interval_key_frame + right, final)
		output_path = output.format(i=index)

		return EbSynthInterval(
			key_frame=interval_key_frame,
			first_frame_is_used=True,
			final_frame_is_used=True,
			first_frame=interval_first_frame,
			final_frame=interval_final_frame,
			output_path=output_path,
		)

	return map(create_one_interval, enumerate(range(first + left, final, step)))


def main():
	""" Command-line editor for EbSynth (EBS) project files. """

	parser = argparse.ArgumentParser(description=main.__doc__)

	# Input and output arguments
	parser.add_argument(
		'-i', '--input',
		help=(
			'path to the input EBS file; '
			'if there is none, the default EbSynth project is used'
		),
		type=Path,
	)
	parser.add_argument(
		'-o', '--output',
		help=(
			'path to the output EBS file; '
			'if there is none, the resulting project is just printed'
		),
		type=Path,
	)

	# Intervals arguments
	parser.add_argument(
		'-ai', '--add-intervals',
		help=(
			'add overlapping frame intervals using the syntax '
			'\"first:final:step:left:right\\{i%%0padding}\\[####].png\" where '
			'`first` is the index of the first frame, '
			'`final` is the index of the final frame, '
			'`step` is the number of frames that separate two keyframes, '
			'`left` is the left extent of each interval, '
			'`right`  is the right extent of each interval, and '
			'`i` is a placeholder for the interval index with `padding` zeroes.'
		),
		type=str,
		nargs='*',
	)

	# Project arguments
	parser.add_argument(
		'-fps', '--frames-per-second',
		help='set the number of frames per second',
		type=float,
	)

	# Images arguments
	parser.add_argument(
		'-kp', '--key-images-path',
		help='set the path to the key images',
		type=str,
	)
	parser.add_argument(
		'-vp', '--video-images-path',
		help='set the path to the video images',
		type=str,
	)
	parser.add_argument(
		'-mp', '--mask-images-path',
		help='set the path to the mask images',
		type=str,
	)

	# Weights arguments
	parser.add_argument(
		'-kw', '--key-images-weight',
		help='set the weight of the key images',
		type=float,
	)
	parser.add_argument(
		'-vw', '--video-images-weight',
		help='set the weight of the video images',
		type=float,
	)
	parser.add_argument(
		'-mw', '--mask-images-weight',
		help='set the weight of the mask images',
		type=float,
	)
	parser.add_argument(
		'-me', '--mask-images-enabled',
		help='set whether or not the mask images are enabled',
		type=bool,
		action=argparse.BooleanOptionalAction,
	)

	# Advanced arguments
	parser.add_argument(
		'-map', '--mapping',
		help='set the mapping value',
		type=float,
	)
	parser.add_argument(
		'-dfl', '--de-flicker',
		help='set the de-flicker value',
		type=float,
	)
	parser.add_argument(
		'-div', '--diversity',
		help='set the diversity value',
		type=float,
	)

	# Performance arguments
	parser.add_argument(
		'-det', '--synthesis-detail',
		help='set the synthesis detail value',
		type=int,
		choices=[1, 2, 3, 4],
	)
	parser.add_argument(
		'-gpu', '--use-gpu',
		help='set whether or not to use the GPU for synthesis',
		type=bool,
		action=argparse.BooleanOptionalAction,
	)

	# Arguments and project parsing
	arguments = parser.parse_args()
	project = read_project_or_return_default(arguments.input)

	# Intervals creation
	for interval_format in (arguments.add_intervals or ()):
		# Separate the arguments and cast them to their expected type
		[first, final, step, left, right, output] = interval_format.split(':')
		project.intervals.extend(create_intervals(
			int(first),
			int(final),
			int(step),
			int(left),
			int(right),
			output.replace('%', ':'),
		))

	def map_argument_to_project_setting(name: str):
		if (value := arguments.__dict__[name]) is not None:
			project.__dict__[name] = value

	map_argument_to_project_setting('frames_per_second')

	map_argument_to_project_setting('key_images_path')
	map_argument_to_project_setting('video_images_path')
	map_argument_to_project_setting('mask_images_path')

	map_argument_to_project_setting('key_images_weight')
	map_argument_to_project_setting('video_images_weight')
	map_argument_to_project_setting('mask_images_weight')
	map_argument_to_project_setting('mask_images_enabled')

	map_argument_to_project_setting('mapping')
	map_argument_to_project_setting('de_flicker')
	map_argument_to_project_setting('diversity')

	map_argument_to_project_setting('synthesis_detail')
	map_argument_to_project_setting('use_gpu')

	write_project_or_print_it(arguments.output, project)


if __name__ == '__main__':
	main()
