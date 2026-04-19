I want to generate book.md from multiple input markdown files.

I want to be able to list an external (outside this repo) path to a directory in which those files will be found.

Then I want to use `[[Obsidian File]]` syntax to say "Look up a file called `Obsidian File.md` using the same methods obsidian uses, somewhere within in the external directory specified above.

Then I want to copy that file into an md directory in this repo, and proceed to find all the `![[image references]]` in that file.

For each of those, I want to search the same directory as above for an image called that, in the same way obsidian does, and then I want to copy that image into an img directory in this repo, and replace the `![[image references]]` in the md file with image references that pandoc will understand, whether it's the `![](path-to-image)` form or some other one.

This will be the basic setup that lets me *develop* and *write* inside obsidian, and then handle the entire process of turning some subset of that writing into a fully formatted *book* in a separate repo, by pointing to the obsidian repo.

If I can get this workflow solid and working stably, I'll be able to take a huge amount of content I've developed over the past few years and start quickly publishing book after book after book.

Generate me a python script that does each of these things.

Give it the following argparse options:

files: names of md files, in desired book order (stdin if not present, one per line).

-i/--input: path to obsidian vault (src of markdown files and images, no default).

-o/--output: path to book directory (dst of markdown files and images, default is 'book').

-1/--list-files: print the paths to the md files you did or did not find in input directory.

-2/--copy-files: copy md files into $output.

-3/--list-images: print the paths to the image files you did or did not find in input directory

-4/--copy-images: copy image files into $output/img

-5/--rewrite-files: rewrite the md files in $output to point to the images in $output/img
