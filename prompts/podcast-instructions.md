# DAILY INTELLIGENCE ROUTINE

Create a high-signal daily news briefing covering important developments from the LAST 24 HOURS.

This is a LIVE WEB RESEARCH task.

NEVER answer from pretrained/model knowledge alone.

# 1. MANDATORY RESEARCH ARCHITECTURE

At the beginning of every run, use the Agent tool to launch SIX independent specialist research agents:

1. AI Researcher
2. Quantum Computing Researcher
3. US Market General News Researcher
4. Czech Republic & Slovakia Researcher
5. PPF Group & CETIN Researcher
6. China Researcher

Launch them in parallel whenever possible.

The main agent acts only as the FINAL EDITOR after the research agents complete.

# 2. MANDATORY LIVE-WEB RULES

Every research agent MUST:

1. Use WebSearch during THIS execution.
2. Perform multiple distinct searches appropriate to its topic.
3. Search specifically for developments from the previous 24 hours.
4. Open promising sources using WebFetch whenever practical.
5. Verify publication/disclosure date.
6. Verify when the underlying EVENT actually happened.
7. Return the actual source URL.
8. Prefer primary/original sources.
9. Reject stories whose freshness cannot be established.
10. Return zero stories rather than filling a section with old news.

DO NOT include an old event merely because a new article about it was published today.

DO NOT use remembered model knowledge as evidence.

DO NOT invent URLs, prices, percentages, timestamps or events.

If live WebSearch is unavailable, report that live research failed instead of generating a briefing from memory.

# 3. GLOBAL STORY DEDUPLICATION — CRITICAL

THE SAME UNDERLYING EVENT MUST NEVER APPEAR IN TWO DIFFERENT SECTIONS.

This applies even if the event logically fits several topics.

Before producing the final result, create an internal list of candidate events and assign each event ONE canonical category.

All other copies must be discarded.

Use the following category precedence:

1. PPF/CETIN-specific event → **PPF Group**
2. China law/regulatory/geopolitical event → **China**
3. AI-specific technological development → **AI**
4. Quantum-specific development → **Quantum Computing**
5. Broad US financial/market event → **US Stock Market → General News**
6. Czech/Slovak-specific event → **Czech Republic & Slovakia**

Examples:

* CETIN announces AI network automation → PPF Group → CETIN, NOT AI
* Chinese government introduces semiconductor export controls → China, NOT AI
* Chinese AI company releases a new foundation model → AI, unless primarily geopolitical/regulatory
* US Fed decision affecting markets → US Stock Market → General News

The FINAL EDITOR must perform this deduplication across ALL agents.

---

# 4. AI

Research major developments involving:

* Anthropic
* OpenAI
* Google / DeepMind
* Microsoft
* Meta
* NVIDIA
* xAI
* Amazon
* Apple
* Mistral
* DeepSeek
* Alibaba / Qwen
* Baidu
* Tencent
* ByteDance
* Zhipu
* Moonshot AI
* other significant AI companies

Prioritize:

## Company announcements

* strategy changes
* investments
* partnerships
* infrastructure
* organizational changes
* major product strategy
* regulation affecting AI companies

## New AI models and capabilities

Track:

* foundation models
* reasoning models
* agents
* coding models
* multimodal systems
* robotics
* image generation
* video generation
* audio
* major new capabilities
* important API capabilities

Ignore insignificant UI changes.

## AI implementation success stories

Search for measurable impact:

* cost savings
* revenue increases
* productivity gains
* automation of workflows
* workforce reduction attributable to AI

Clearly distinguish claims vs verified results.

## Difficult problems solved with AI

Include progress in:

* medicine
* biology
* mathematics
* engineering
* materials science
* climate science
* robotics
* scientific discovery

Distinguish:

* simulation
* preprint
* peer-reviewed research
* animal study
* clinical trial
* approved treatment

## AI chips and hardware

Track:

* NVIDIA
* AMD
* Intel
* IBM
* Google
* AWS
* Microsoft
* Cerebras
* Groq
* Huawei
* other semiconductor firms

Include:

* new chips
* performance breakthroughs
* manufacturing
* export restrictions
* datacenter deployments

---

# 5. QUANTUM COMPUTING

Prioritize:

* new quantum processors
* logical qubits
* error correction
* fault tolerance
* meaningful qubit advances
* algorithms
* quantum networking
* commercially relevant applications
* major scientific breakthroughs
* major investment

Track:

* IBM
* Google
* Microsoft
* Quantinuum
* IonQ
* D-Wave
* major research institutions

Be skeptical of exaggerated claims.

---

# 6. US STOCK MARKET

This top-level category contains ONE section.

## 6.1 GENERAL NEWS

Include only significant developments such as:

* major index moves
* Federal Reserve decisions
* inflation / employment data
* major economic releases
* earnings surprises
* guidance changes
* bankruptcies
* major IPOs
* regulatory actions
* unusually large stock moves
* major tech-stock developments
* AI-related market impacts

Explain causes when known.

Separate confirmed causes from speculation.

Ignore normal fluctuations.

---

# 7. CZECH REPUBLIC & SLOVAKIA

Actively search Czech and Slovak sources.

Prioritize practical impact.

## Economy

* inflation
* interest rates
* wages
* energy costs
* unemployment
* policy changes

## Laws and regulation

* proposed laws
* approvals
* effective laws
* regulations

## Personal finance (high priority)

* taxes
* pensions
* mortgages
* subsidies
* insurance
* benefits
* savings products
* housing costs

## Housing

* mortgages
* rent regulation
* property taxes
* housing programs

## Technology

* AI
* telecom
* cybersecurity
* digital government

---

# 8. PPF GROUP

PPF Group is ONE top-level category.

CETIN is the HIGHEST PRIORITY within PPF.

Use two subcategories:

## 8.1 CETIN — PRIORITY

Track:

* fibre deployment
* 5G
* infrastructure investment
* modernization
* contracts
* regulation
* spectrum
* financial results
* partnerships
* automation
* cybersecurity
* AI in networks

Search Czech-language sources extensively.

## 8.2 OTHER PPF GROUP

Track:

* ownership changes
* investments
* financing
* strategy
* executive changes
* telecom and infrastructure
* major partnerships
* regulation
* litigation

If CETIN is involved, classify under CETIN.

---

# 9. CHINA

Focus on mainland China.

Prioritize meaningful developments.

## Laws and regulation

* trade
* export controls
* foreign investment
* data regulation
* cybersecurity
* capital controls
* taxation
* visas
* banking

## International relations

* US-China
* EU-China
* semiconductor restrictions
* trade disputes

## Technology and science

* AI
* semiconductors
* quantum computing
* robotics
* space
* energy
* major scientific advances

## Major events

* economic events
* disasters
* national policy changes

---

# 10. FINAL EDITOR PROCESS

After all research agents finish:

1. Combine all candidate stories
2. Normalize names
3. Remove duplicates across categories
4. Assign ONE canonical category per event
5. Verify 24-hour freshness
6. Verify at least one real source
7. Reject unverifiable stories
8. Rank by importance
9. Do not add external knowledge
10. Do not fabricate missing content

Perform final cross-category duplicate check.

---

# 11. FINAL OUTPUT FORMAT

Output ONLY a multi-level Markdown list.

Start:

# Daily News — YYYY-MM-DD

Then:

1. **AI**

   * [One concise sentence.](ACTUAL_SOURCE_URL)

2. **Quantum Computing**

   * [One concise sentence.](ACTUAL_SOURCE_URL)

3. **US Stock Market**

   * **General News**

     * [One concise sentence.](ACTUAL_SOURCE_URL)

4. **Czech Republic & Slovakia**

   * [One concise sentence.](ACTUAL_SOURCE_URL)

5. **PPF Group**

   * **CETIN**

     * [One concise sentence.](ACTUAL_SOURCE_URL)
   * **Other PPF Group**

     * [One concise sentence.](ACTUAL_SOURCE_URL)

6. **China**

   * [One concise sentence.](ACTUAL_SOURCE_URL)

Each item must be exactly ONE sentence and fully hyperlinked.

If no developments exist, output:

* No material developments found.

---

# 12. IMPORTANCE PRIORITY

Rank by:

1. Financial impact
2. Market-moving significance
3. Technological/scientific breakthroughs
4. AI capability advances
5. Regulatory/legal impact
6. Geopolitical impact
7. General interest

---

# 13. REPOSITORY SAFETY

DO NOT modify the GitHub repository.
DO NOT create files, commits, branches, or pull requests.
