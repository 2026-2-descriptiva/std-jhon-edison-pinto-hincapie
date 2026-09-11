from collections import defaultdict
from pathlib import Path
import re
import shutil


DATA_FOLDER = "PRE_02_mapreduce/data"
INPUT_FOLDER = "PRE_02_mapreduce/temp/input"
OUTPUT_FOLDER = "PRE_02_mapreduce/temp/output"


def _resolve_path(path):
	return Path(path)


def initialize_folder(folder):
	_resolve_path(folder).mkdir(parents=True, exist_ok=True)


def delete_folder(folder):
	folder_path = _resolve_path(folder)
	if folder_path.exists():
		shutil.rmtree(folder_path)


def generate_file_copies(number_of_copies):
	source_folder = _resolve_path(DATA_FOLDER)
	if not source_folder.exists():
		source_folder = Path("data")
	input_folder = _resolve_path(INPUT_FOLDER)
	initialize_folder(input_folder)

	source_files = sorted(path for path in source_folder.iterdir() if path.is_file())
	for copy_number in range(number_of_copies):
		for source_file in source_files:
			destination = input_folder / f"{copy_number:06d}-{source_file.name}"
			shutil.copyfile(source_file, destination)


def mapper(line):
	words = re.findall(r"[a-z]+", line.lower())
	return [(word, 1) for word in words]


def reducer(word, counts):
	return word, sum(counts)


def hadoop(input_folder, output_folder, mapper_fn, reducer_fn):
	input_path = _resolve_path(input_folder)
	output_path = _resolve_path(output_folder)
	mapped = defaultdict(list)

	for input_file in sorted(path for path in input_path.iterdir() if path.is_file()):
		with input_file.open("r", encoding="utf-8") as file:
			for line in file:
				for word, count in mapper_fn(line):
					mapped[word].append(count)

	reduced = [reducer_fn(word, mapped[word]) for word in sorted(mapped)]
	initialize_folder(output_path)
	with (output_path / "part-00000").open("w", encoding="utf-8") as file:
		for word, count in reduced:
			file.write(f"{word}\t{count}\n")
