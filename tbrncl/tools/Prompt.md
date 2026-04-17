Whenever I type a bible chapter into this chat, like "Genesis 3" for example, I want you to output XeLaTeX that generates a template for that chapter's translation. The template should look something like this (I'll speak markdown, but I want you to generate XeLaTeX.

```

## Genesis 3

---

> 1 א  וְהַנָּחָשׁ, הָיָה עָרוּם, מִכֹּל חַיַּת הַשָּׂדֶה, אֲשֶׁר עָשָׂה יְהוָה אֱלֹהִים; וַיֹּאמֶר, אֶל-הָאִשָּׁה, אַף כִּי-אָמַר אֱלֹהִים, לֹא תֹאכְלוּ מִכֹּל עֵץ הַגָּן.

> 1 And the snake was slier than every animal of the field that YHWH God had made, and he said to the woman, “Has God indeed said you may not eat from any tree of the garden?”

0: 

---

> 2 And the woman said to the snake, “We may eat from the fruit of the trees of the garden.

> 2 ב  וַתֹּאמֶר הָאִשָּׁה, אֶל-הַנָּחָשׁ:  מִפְּרִי עֵץ-הַגָּן, נֹאכֵל.

0: 
```

And then continue in this format for the rest of the chapter.

The numbers (0 here) that appear before the Hebrew are where I'll be typing a new simpler translation that attempts to include all the different layers of data that are provided by books like (1) The Bible with Sources Revealed (i.e., source coloring), (2) Commentary on the Torah (i.e., footnotes to give background), and (3) The Hidden Book in the Bible / The Book of J (i.e., the separation of the sources into linear narratives, starting with J.)

In LateX, I want you to do something like (just giving the general idea here)

```
\J{

}
```

Wrapping around the text that's by J, and similarly for E, P, RJE, and R.

J should be green, non-bold, non-italic.
E should be green, bold, non-italic.
P should be blue, bold, non-italic.
R should be blue, non-bold, non-italic, with a light blue background screen.
RJE should be green, non-bold, non-italic, with a light green background screen.
The Book of Records sources should be blue, non-bold, italic.
Other sources should be green, non-bold, italic.
Each page should have a legend at the top to remind the reader which source is which.

Begin by doing this for Genesis 2.

