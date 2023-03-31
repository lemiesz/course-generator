# Description

A course generator based on GPT-4. This will take a topic and a request number of Learning Objectives.
It will then generate a course based on that input.

you can generator course as either JSON files or as HTML

## Usage

```bash
python main.py --topic "Intro To Web Development" --num_of_los 3 --output-folder web-dev-course --output_type=html
```

This will generate a intro to web development course with 3 learning objectives. The output file types will be html
