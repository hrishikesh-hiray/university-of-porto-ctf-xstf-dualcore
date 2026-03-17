# CTF Writeup: Left Behind

**Challenge Name:** Left Behind  
**Author:** BoneTeixeira  
**Category:** OSINT / Geolocation  
**Flag Format:** `upCTF{name_surname}`  
**Flag:** `upCTF{John_Stephen}`

---

## Challenge Description

> *"I was passing through this street when I stopped to take a photo. It's a place people walk through every day, often without noticing much beyond what's right in front of them. Somewhere along this street, a name has been left behind - quietly, deliberately, and meant to last. That name is what you're looking for."*

We are given a single image (`left_behind.png`) showing a busy pedestrian street lined with shops, red brick buildings, and people going about their day. Our task is to identify a **name** that has been permanently and deliberately left behind somewhere along this street.

---

## Step 1: Image Analysis & Location Identification

The first step in any OSINT image challenge is to **geolocate the photograph**.

### Visual Cues Identified

Upon close inspection of the image, several key identifiers are visible:

| Clue | Detail |
|------|--------|
| **Arch sign (top of image)** | Reads *"Welcome to ... Street"* — partially obscured by the fish-eye/wide-angle lens distortion |
| **Architecture style** | Victorian-era red brick buildings typical of central London |
| **Street layout** | Narrow pedestrian-only cobblestone shopping street |
| **Shop fronts** | Fashion boutiques, including what appears to be a "Lastin" (Lasting?) sign on the right |
| **Street bollards** | Classic black cast-iron bollards characteristic of London pedestrian zones |
| **Greenery** | Window boxes with plants, common in London's Soho area |

### Reading the Arch

The most direct clue is the **decorative arch/gate** at the top of the image. Despite the wide-angle distortion, the lettering resolves to:

```
WELCOME TO CARNABY STREET
```

**Location confirmed: Carnaby Street, Soho, London, UK**

Carnaby Street is one of London's most iconic pedestrian shopping streets, made famous during the Swinging Sixties as the epicentre of British fashion and youth culture.

---

## Step 2: Interpreting the Challenge Description

The description contains several deliberate keywords:

- *"a name has been left behind"* → Not graffiti, not a shop — something **memorial** in nature
- *"quietly"* → Not a major landmark; easy to walk past
- *"deliberately"* → Intentionally placed, officially sanctioned
- *"meant to last"* → A **permanent fixture**: plaque, engraving, or official marker
- *"people walk through every day, often without noticing"* → It blends into the environment — a **blue heritage plaque** or embedded marker

This phrasing almost certainly describes an **English Heritage Blue Plaque** or a similar permanent commemorative installation — the kind of thing embedded in a wall that pedestrians routinely ignore.

---

## Step 3: Researching Carnaby Street's Historical Figures

Carnaby Street has significant cultural history. A search for notable figures commemorated on the street leads to one dominant name:

### John Stephen (1934–2004)

> **"The Man Who Invented the Sixties"** — *The Guardian*

John Stephen was a Scottish fashion designer and entrepreneur who is widely credited with **transforming Carnaby Street** from an unremarkable backstreet into the world's most famous fashion destination.

Key facts:
- Born in Glasgow, Scotland in 1934
- Opened his first shop on Carnaby Street in **1957** (His Clothes, at No. 5)
- At his peak, owned **15 boutiques** on Carnaby Street simultaneously
- Pioneered affordable, bold men's fashion for the working class youth market
- Attracted clientele including The Beatles, The Rolling Stones, and The Kinks
- Earned the title **"King of Carnaby Street"**
- Died in 2004

### The Blue Plaque

A **commemorative blue plaque** was erected on Carnaby Street in John Stephen's honour. Blue plaques are installed by English Heritage (and the Greater London Authority) on buildings of historical significance — they are permanent, unobtrusive, and routinely walked past without notice.

This matches every element of the challenge description:
- ✅ A **name** left behind
- ✅ **Quietly** — a small plaque on a wall
- ✅ **Deliberately** — officially sanctioned and installed
- ✅ **Meant to last** — permanent installation
- ✅ People walk past it **every day without noticing**

---

## Step 4: Flag Construction

The challenge format specifies:

```
upCTF{name_surname}
```

With the example `upCTF{Jane_Doe}` confirming:
- First name, underscore, surname
- Standard capitalisation (Title Case)

Applying this to our answer:

```
upCTF{John_Stephen}
```

---

## Flag

```
upCTF{John_Stephen}
```

---

## Tools & Techniques Used

| Tool / Technique | Purpose |
|-----------------|---------|
| **Visual image analysis** | Reading the partial arch text, identifying architecture style |
| **OSINT / Geolocation** | Confirming the street as Carnaby Street, London |
| **Keyword analysis** | Parsing "quietly, deliberately, meant to last" → heritage plaque |
| **Historical research** | Identifying John Stephen and his blue plaque on Carnaby Street |
| **Google / Wikipedia** | Cross-referencing Carnaby Street history and notable commemorations |

---

## Key Takeaways

1. **Read the environment carefully.** The arch sign at the top of the image is the most important clue and directly identifies the location.

2. **Parse the challenge text for meta-clues.** Words like "quietly," "deliberately," and "meant to last" are not flavour — they describe the *type* of object you're looking for. In this case, a permanent official memorial rather than graffiti or signage.

3. **Think about what gets overlooked.** The challenge specifically says people "walk through every day without noticing." This narrows the answer to small, embedded, official installations — exactly what a heritage plaque is.

4. **OSINT chains are iterative.** Location → Historical significance → Named commemorations → Flag. Each step feeds the next.

---

Writeup by:Hrishikesh

*Challenge from: upCTF*
