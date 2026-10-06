# My prep notes

Personal notes for the Analyst - TMT (Media CoE) role, Bain Capability Network, New Delhi.
Not part of the project. Delete this file before sending the folder anywhere.

---

## What the process actually is

CV screen → online assessment (SOVA / TestGorilla / BOAT-style) → round one: two 30-45 min interviews,
case + experience → final round with partners.

Roughly 1.5% of applicants get an offer overall, but it's closer to 15-20% for people who make it to
the case interviews. So the filtering happens at the CV screen and the assessment. The project helps
with the first one and with the experience interview. It does nothing for the assessment, which I need
to prepare separately.

## The 90 second version

Don't memorise this word for word. Learn the order and the four numbers.

> I wanted to test something I kept reading, which is that India is one of the world's biggest
> entertainment markets. By audience it clearly is. So I built a database across six markets to see
> whether it's also one by money.
>
> I took time-spent data from Ofcom, Nielsen, eMarketer and DataReportal, revenue data from PwC,
> Newzoo, IFPI and FICCI-EY, and normalised everything into one number: dollars of industry revenue
> per 1,000 hours of attention. That makes a $30 billion market comparable to a $2 trillion one.
>
> India comes out at about $3.60. The US is about $307. So roughly an 86x gap, against an income gap
> of about 11x. And the reason isn't that Indians won't pay. India already has 216.5 million paid OTT
> subscriptions, the third largest base in the world. It's that each one is worth $7.30 a year.
>
> So for an operator here, user acquisition is no longer the scarce input. Yield is. Which in practice
> means connected TV, where Indian ad revenue grew 42% last year while linear TV fell 10%, and formats
> with no content amortisation drag, like live events and gaming.
>
> The number I'd most want to stress test is my time-spent data, because it comes from measurement
> systems that were never designed to be compared with each other. My revenue numbers are audit grade.
> My denominators aren't.

Four numbers to remember: 3.60, 307, 216.5 million, 7.30.

## Questions I should expect

**"Where does the 86x come from?"**
Numerator is MPA's screen economy per capita, $8.4 for India and $889 for the US. Denominator is my
five-format time sum annualised, 2,403 hours for India and 2,908 for the US. $3.56 and $306.69.
If I use the published all-media time measure instead, India becomes $2.9 and the US $222. The ratio
hardly moves, which is why I put both in the workbook.

**"Your time data is inconsistent across countries. Doesn't that break the whole thing?"**
The denominator is weak and I say so. Ofcom measures TV-set viewing at home, Nielsen measures the TV
screen, DataReportal is self-reported internet time. The numerator is solid. So I treat the level as
an estimate and the direction as the finding. There's a sensitivity query and a slide for exactly
this, and the ranking holds under both denominators.

**"Why only six markets?"**
Two mature western markets with different regulation (US, UK), two Asian markets with very different
format mixes (Japan is TV-first, Korea is gaming-first), one emerging market with world-scale
attention (India), one with world-scale social usage (Brazil). Six is the smallest set I could find
that separates format mix, income level and market structure as distinct variables.

**"What would you do differently with a real client?"**
Two things. Get primary data, because secondary time-spent data is the weakest part of this. And
rebuild the revenue side from the client's own P&L instead of industry averages, because averages
hide the segment differences that actually decide where money should go.

**"What's the weakest part?"**
The India OTT subscription count. 216.5 million includes bundled and telecom-included subscriptions,
so the true direct-paid ARPU is probably higher than $7.30. That would strengthen my conclusion
rather than weaken it, but I'd want the split. Also, live events revenue outside India and the US is
scaled from estimates rather than measured.

**"How long did this take?"**
Three weeks, mostly on data collection. The time-spent data took the longest because no single source
covers all six markets.

## If they ask how I built it

Answer honestly. I built the analysis and made every judgement call myself. I used tooling to move
fast on the code, the same way I'd use any analyst tool, and I can explain every query, every
assumption and every number in it. Then offer to open the database and run a query live. That's the
strongest possible answer and it's also true.

If I can't explain a part, I shouldn't ship that part.

## Things to practise separately

- **Assessment:** data interpretation, percentages and ratios under time pressure, chart questions.
  Three or four sessions a week for a few weeks.
- **Cases:** Bain's cases are candidate-led and conversational. Aim for 20+, including a few in
  media or PE diligence.
- **Experience interview:** three STAR stories with numbers. This project is one. I need two more
  from internships, college or competitions.

## Before I submit

- [ ] Name and date filled in everywhere
- [ ] Deck exported to PDF
- [ ] $3.56 and $306.69 checked by hand
- [ ] Walkthrough rehearsed three times, out loud, timed
- [ ] Digital ad split in the extras project rechecked or stated as a range

## 90-second walkthrough (dashboard first)

"We took six markets and built two parallel tables, minutes of attention per day and dollars of
screen revenue, 2020 and 2025. Divide one by the other and you get a monetisation index: revenue per
thousand hours of attention. The US sits at 306 dollars, India at 3.56. That is an 86x gap on the
same behaviour.

The interesting part is the direction of travel. Attention is not shrinking anywhere, it is moving
inside the screen. Linear TV loses 13 minutes a day in India and 81 in the UK, and streaming picks
up more than that in each case. Total time on screens is up in every market we cover.

So the story is not that India watches less. India watches about as much as the US. India just
monetises it at about one percent of the rate, which is why every global platform is here and the
domestic revenue pool is still small."

Then stop. Let them ask.

## Questions I should expect

**"Your time data comes from different measurement systems."**
Yes, and that is why the time and money tables are separate and never multiplied by each other
across sources. There is a query that re-runs the whole ranking on a single published all-media
denominator instead of the five-format sum. India stays last, the US stays first, only Japan and
Korea swap places.

**"Why is India's OTT ARPU 10 dollars when PwC says 7.30?"**
PwC's number is subscription revenue per subscription. Ours is total OTT revenue including
advertising-tier and ad-supported minutes, divided by paid subscriptions. Different definitions, and
the query says so in a comment. Either can be defended as long as you name which one you are using.

**"2020 was COVID. Isn't that CAGR just recovery?"**
For theatrical, live events and music, partly yes. The query flags it. Streaming and digital
advertising grew straight through 2020, so their CAGRs are not recovery artefacts.

**"What would you do with another week?"**
Rebuild the digital advertising split from GroupM or WPP data instead of the estimate in extras, and
add two more markets (Indonesia and Mexico) to test whether the double-growth pattern in gaming and
streaming holds outside the six.
