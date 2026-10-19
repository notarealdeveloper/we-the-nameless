
| Overall place | Book | Authorship rank | Narrative rank | Harmonic mean |
|---:|---|---:|---:|---:|
| 1 | **Genesis** | 3 | 1 | **1.500** |
| 2 | **Samuel** | 1 | 8 | **1.778** |
| 3 | **Exodus** | 4 | 2 | **2.667** |
| 4 | **Judges** | 2 | 7 | **3.111** |
| 5 | **Leviticus** | 5 | 3 | **3.750** |
| 6 | **Numbers** | 6 | 4 | **4.800** |
| 7 | **Deuteronomy** | 8 | 5 | **6.154** |
| 8 | **Joshua** | 9 | 6 | **7.200** |
| 9 | **Kings** | 7 | 9 | **7.875** |

---

## The Olympics

First rank the books by the average age of their written content, assuming Hezekian P:

Samuel → Judges → Genesis → Exodus → Leviticus → Numbers → Kings → Deuteronomy → Joshua.

Then rank them by the age of the events they narrate:

Genesis → Exodus → Leviticus → Numbers → Deuteronomy → Joshua → Judges → Samuel → Kings.

We now have a general problem: how do we combine \(N\) scores measured in possibly different units? Adding meters to kilograms is easy. Making the answer mean something takes another step.

The simplest approach is to discard the units. Convert each score into its position in a distribution—a CDF score—or, simpler still, replace it with its integer rank.

Think of an Olympics with \(N\) events. We want gold to count for a lot, silver and bronze to remain impressive, and finishing last in another event to do limited damage. An especially simple rule is to award \(1/r\) points for rank \(r\), then average the points. Expressing the result back on the rank scale gives the harmonic mean:

\[
H=\left(\frac1N\sum_{i=1}^{N}\frac1{r_i}\right)^{-1}.
\]

Strictly, the qualitative wishes alone do not uniquely determine this formula; reciprocal scoring supplies the additional assumption. It gives precisely the behavior we wanted: excellence matters more than mediocrity hurts.

Applied to our two rankings, this yields:

Genesis → Samuel → Exodus → Judges → Leviticus → Numbers → Deuteronomy → Joshua → Kings.