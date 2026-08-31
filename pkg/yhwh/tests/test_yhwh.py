import re
import yhwh
S=r'''\Chapter{1}
\Verse{1}{\hJ{בְּ אֵשׁ}\hE{ וַיֹּאמֶר}}{\eJ{In Fire}\eE{ and he said}}{}
\Verse{2}{\hP{אֵשׁ}}{\eP{FIRE}}{}'''
def corpus(): return yhwh.model.corpus_from_verses(yhwh.parse_tex_text(S,book='Test',chapter=1))
def test_parse_spans():
 c=corpus(); v=c.verses[0]; assert v.sources==('J','E'); assert v.hebrew_spans[0].source=='J'; assert 'In Fire' in v.english
def test_english_case_and_regex():
 c=corpus(); assert len(c.english('fire'))==2; assert len(c.english(r'^In',regex=True))==1
def test_hebrew_ignores_spaces_niqqud():
 c=corpus(); assert len(c.hebrew('באש'))==1; assert len(c.hebrew('ב אֵשׁ'))==1; assert len(c.hebrew('באש',spaces=True))==0
def test_global_niqqud():
 yhwh.set_niqqud(True); assert yhwh.get_niqqud(); yhwh.set_niqqud(False)
def test_frequency_and_source():
 c=corpus(); f=c.frequency('english',books=['Test']); assert isinstance(f,yhwh.Frequency); assert f['fire']==2
 fs=c.frequency('english',books=['Test'],by_source=True); assert fs['J']['in']==1 and fs['P']['fire']==1
def test_word_split_only_space():
 assert yhwh.words("father-in-law don't odd—dash")==['father-in-law',"don't",'odd—dash']
def test_evidence():
 c=corpus(); m=yhwh.train(c,language='english',books=['Test'],sources=('J','E','P')); r=m.score('fire'); assert set(r.posteriors)=={'J','E','P'}
