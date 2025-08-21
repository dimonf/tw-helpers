#!/usr/bin/env python3
import argparse
import json
import random
from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Sequence


def tw5_timestamp(dt: datetime) -> str:
	utc = dt.astimezone(timezone.utc)
	return utc.strftime("%Y%m%d%H%M%S") + f"{int(utc.microsecond/1000):03d}"


def quote_tag_if_needed(tag: str) -> str:
	if " " in tag or "[" in tag or "]" in tag:
		return f"[[{tag}]]"
	return tag


def build_tags_field(tags: Sequence[str]) -> str:
	if not tags:
		return ""
	return " ".join(quote_tag_if_needed(t) for t in tags)


# --------------------------- Lorem generation --------------------------- #

_LOREM_WORDS = (
	"lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident sunt in culpa qui officia deserunt mollit anim id est laborum"
	.split()
)


def _generate_sentence(min_words: int, max_words: int) -> str:
	word_count = random.randint(min_words, max_words)
	words = [random.choice(_LOREM_WORDS) for _ in range(word_count)]
	text = " ".join(words)
	text = text.capitalize()
	# sprinkle a comma sometimes
	if word_count >= 8 and random.random() < 0.35:
		comma_pos = random.randint(3, max(3, word_count - 3))
		parts = text.split(" ")
		parts[comma_pos] = parts[comma_pos] + ","
		text = " ".join(parts)
	return text + "."


def generate_lorem(paragraphs: int, min_sentences: int, max_sentences: int, min_words: int, max_words: int) -> str:
	result_paragraphs: List[str] = []
	for _ in range(paragraphs):
		sentence_count = random.randint(min_sentences, max_sentences)
		sentences = [_generate_sentence(min_words, max_words) for _ in range(sentence_count)]
		result_paragraphs.append(" ".join(sentences))
	return "\n\n".join(result_paragraphs)


# ---------------------------- CLI and main ------------------------------ #


def _split_csv(values: Iterable[str]) -> List[str]:
	result: List[str] = []
	for v in values:
		for part in v.split(","):
			p = part.strip()
			if p:
				result.append(p)
	return result


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Generate a JSON array of TiddlyWiki tiddlers for import."
	)
	parser.add_argument("-n", "--num", type=int, required=True, help="Number of tiddlers to generate")
	parser.add_argument("-o", "--output", type=str, default="", help="Output file (default: stdout)")
	parser.add_argument("-p", "--prefix", type=str, default="Tiddler", help="Title prefix (default: Tiddler)")
	parser.add_argument("--start-index", type=int, default=1, help="Starting index for titles (default: 1)")
	parser.add_argument("--text", type=str, default="This is tiddler {i}.", help="Body text template; placeholders: {i}, {title}")
	parser.add_argument("--tag", dest="fixed_tags", action="append", default=[], help="Fixed tag to add (repeatable or comma-separated)")
	parser.add_argument("--type", dest="content_type", type=str, default="text/vnd.tiddlywiki", help="Content type (default: text/vnd.tiddlywiki)")
	parser.add_argument("--creator", type=str, default="", help="creator field (optional)")
	parser.add_argument("--modifier", type=str, default="", help="modifier field (optional)")
	parser.add_argument("--increment-seconds", type=int, default=0, help="Seconds to add between each tiddler timestamp")

	# Random tags
	parser.add_argument("--random-tags", action="store_true", help="Enable random tag assignment from a pool")
	parser.add_argument("--tag-pool", action="append", default=[], help="Tag pool (repeatable or comma-separated). If omitted, a default pool is used.")
	parser.add_argument("--min-tags", type=int, default=0, help="Minimum number of random tags per tiddler")
	parser.add_argument("--max-tags", type=int, default=3, help="Maximum number of random tags per tiddler")

	# Lorem text generator
	parser.add_argument("--lorem", action="store_true", help="Generate lorem ipsum text instead of --text template")
	parser.add_argument("--lorem-paragraphs", type=int, default=1, help="Number of paragraphs per tiddler (default: 1)")
	parser.add_argument("--lorem-min-sentences", type=int, default=3, help="Minimum sentences per paragraph (default: 3)")
	parser.add_argument("--lorem-max-sentences", type=int, default=7, help="Maximum sentences per paragraph (default: 7)")
	parser.add_argument("--lorem-min-words", type=int, default=5, help="Minimum words per sentence (default: 5)")
	parser.add_argument("--lorem-max-words", type=int, default=12, help="Maximum words per sentence (default: 12)")

	# Reproducibility
	parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible output")

	args = parser.parse_args()

	if args.seed is not None:
		random.seed(args.seed)

	now = datetime.now(timezone.utc)

	# Build fixed tags list (from --tag, allowing comma-separated)
	fixed_tags: List[str] = _split_csv(args.fixed_tags)

	# Build tag pool if random tags requested
	if args.random_tags:
		pool = _split_csv(args.tag_pool)
		if not pool:
			pool = [
				"Todo",
				"Note",
				"Work",
				"Personal",
				"Idea",
				"Project",
				"Reading",
				"Reference",
				"Draft",
				"Meeting",
				"Research",
				"Archive",
			]
		# Ensure bounds make sense
		min_tags = max(0, args.min_tags)
		max_tags = max(min_tags, args.max_tags)
	else:
		pool = []
		min_tags = 0
		max_tags = 0

	tiddlers = []
	for idx in range(args.start_index, args.start_index + args.num):
		title = f"{args.prefix} {idx}"
		t = now + timedelta(seconds=(idx - args.start_index) * args.increment_seconds)
		ts = tw5_timestamp(t)

		# Text
		if args.lorem:
			text_value = generate_lorem(
				paragraphs=max(1, args.lorem_paragraphs),
				min_sentences=max(1, args.lorem_min_sentences),
				max_sentences=max(args.lorem_min_sentences, args.lorem_max_sentences),
				min_words=max(1, args.lorem_min_words),
				max_words=max(args.lorem_min_words, args.lorem_max_words),
			)
		else:
			text_value = args.text.format(i=idx, title=title)

		# Tags per tiddler
		if args.random_tags and pool:
			available_pool = [p for p in pool if p not in fixed_tags]
			k = random.randint(min_tags, min(max_tags, len(available_pool)))
			random_tags = random.sample(available_pool, k=k)
			all_tags = fixed_tags + random_tags
		else:
			all_tags = fixed_tags

		tiddler = {
			"title": title,
			"text": text_value,
			"created": ts,
			"modified": ts,
			"tags": build_tags_field(all_tags),
			"type": args.content_type,
		}
		if args.creator:
			tiddler["creator"] = args.creator
		if args.modifier:
			tiddler["modifier"] = args.modifier
		tiddlers.append(tiddler)

	output_json = json.dumps(tiddlers, ensure_ascii=False, indent=2)
	if args.output:
		with open(args.output, "w", encoding="utf-8") as f:
			f.write(output_json)
	else:
		print(output_json)


if __name__ == "__main__":
	main()

