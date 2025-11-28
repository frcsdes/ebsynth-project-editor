import argparse

from pathlib import Path
from typing import Iterable

from ebs import (
    EbSynthInterval,
    read_project_or_return_default,
    write_project_or_print_it,
)


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
