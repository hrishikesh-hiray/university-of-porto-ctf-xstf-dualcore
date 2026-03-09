# upCTF Misc - Deoxyribonucleic acid

## Challenge Info
- Category: Misc
- Name: Deoxyribonucleic acid
- Author tag shown: `abreu22`
- Hint text: `Returning to fundamental silliness, Goldman et al. (2013)`
- Flag format: `upCTF{...}` (case-sensitive)

## Given Data
The file `sample.txt` contains:
1. A DNA-like string made of `A/C/G/T`.
2. A transition table:

```text
#           | 0 | 1 | 2
#  ---------|---|---|---
#     A     | C | G | T
#     C     | G | T | A
#     G     | T | A | C
#     T     | A | C | G
```

This table is the same style used in Goldman et al. DNA storage encoding: each ternary digit (`0,1,2`) is mapped to the next nucleotide based on the previous nucleotide.

## Core Observation
The table lets us reverse each adjacent nucleotide pair back into one trit.
- If previous base is `A` and next is `C`, trit is `0`.
- If previous base is `A` and next is `G`, trit is `1`.
- If previous base is `A` and next is `T`, trit is `2`.
- Same logic for previous `C/G/T` rows.

So for a DNA string of length `N`, we get `N-1` trits by reading pairwise transitions.

## Step 1 - Recover Ternary Stream from DNA
Using the DNA sequence from `sample.txt`, decode transitions to trits.

PowerShell used:

```powershell
$seq='ACTCTACGAGTCTACAGAGTCGTCGTATCAGTCTCACGTGAGCGAGTATACAGTGTCGAGCGTGCGACTCGCTACAGAGTCGCTGTAGCACGAGTCTAGTGTGTCGATCGAGTGTAGTCTGTCGTCGTCGCTGTAGCACGAGTATAGTCTGTCGTAGTAGCAGTATGATAGAGCA'
$map=@{
  'A'=@{'C'='0';'G'='1';'T'='2'}
  'C'=@{'G'='0';'T'='1';'A'='2'}
  'G'=@{'T'='0';'A'='1';'C'='2'}
  'T'=@{'A'='0';'C'='1';'G'='2'}
}
$trits=''
for($i=1;$i -lt $seq.Length;$i++){
  $prev=$seq[$i-1]
  $cur=$seq[$i]
  $trits += $map[[string]$prev][[string]$cur]
}
"len=$($seq.Length), trits=$($trits.Length)"
$trits
```

Output summary:
- DNA length = `175`
- Trit count = `174`

Recovered trits:

```text
011100011011002111010010002121011120002112011002002102010112002201011021002111010212001220011011010202010121011020010112010010010212001220011002010112010001001221002212011122
```

## Step 2 - Determine Grouping
A key clue is total trit count:
- `174` is divisible by `6`
- `174 / 6 = 29`

Goldman-style pipelines can represent data in ternary chunks; here, 6-trit chunks decode cleanly.

Each 6-trit chunk interpreted as a base-3 integer yields values in `[0, 728]`; in this challenge, they map directly to printable ASCII bytes.

## Step 3 - Decode 6-Trit Chunks to ASCII
PowerShell used:

```powershell
$tr='011100011011002111010010002121011120002112011002002102010112002201011021002111010212001220011011010202010121011020010112010010010212001220011002010112010001001221002212011122'

function T([string]$s){
  $n=0
  foreach($c in $s.ToCharArray()){
    $n=$n*3+([int][string]$c)
  }
  $n
}

$vals=@()
for($i=0;$i -lt $tr.Length;$i+=6){
  $vals += (T $tr.Substring($i,6))
}

$vals -join ','
$txt = -join ($vals | ForEach-Object {
  if($_ -ge 32 -and $_ -le 126){ [char]$_ } else { '.' }
})
$txt
```

Important intermediate values:

```text
117,112,67,84,70,123,68,110,65,95,73,115,67,104,51,112,101,97,114,95,84,104,51,110,95,82,52,77,125
```

ASCII result:

```text
upCTF{DnA_IsCh3pear_Th3n_R4M}
```

## Final Flag

```text
upCTF{DnA_IsCh3pear_Th3n_R4M}
```

## Why This Works
- The provided table exactly defines a deterministic finite-state mapping from trits to nucleotides.
- Reversing adjacent nucleotide transitions reconstructs the trit stream losslessly.
- The challenge data is structured so that fixed 6-trit symbols convert directly to ASCII for the final plaintext.

## Notes and Pitfalls
- Do not attempt direct `A/C/G/T -> bits` mapping first; it is not the intended path here.
- The first nucleotide acts as initial state context; trits come from transitions between consecutive bases.
- In PowerShell, custom base-3 conversion is safer than `[Convert]::ToInt32(value, 3)` since base 3 is not supported there.

## Minimal Repro Script (All-in-One)

```powershell
$seq='ACTCTACGAGTCTACAGAGTCGTCGTATCAGTCTCACGTGAGCGAGTATACAGTGTCGAGCGTGCGACTCGCTACAGAGTCGCTGTAGCACGAGTCTAGTGTGTCGATCGAGTGTAGTCTGTCGTCGTCGCTGTAGCACGAGTATAGTCTGTCGTAGTAGCAGTATGATAGAGCA'
$map=@{
  'A'=@{'C'='0';'G'='1';'T'='2'}
  'C'=@{'G'='0';'T'='1';'A'='2'}
  'G'=@{'T'='0';'A'='1';'C'='2'}
  'T'=@{'A'='0';'C'='1';'G'='2'}
}
function T([string]$s){
  $n=0
  foreach($c in $s.ToCharArray()){
    $n=$n*3+([int][string]$c)
  }
  $n
}
$tr=''
for($i=1;$i -lt $seq.Length;$i++){
  $tr += $map[[string]$seq[$i-1]][[string]$seq[$i]]
}
$out=''
for($i=0;$i -lt $tr.Length;$i+=6){
  $out += [char](T $tr.Substring($i,6))
}
$out
```

Expected output:

```text
upCTF{DnA_IsCh3pear_Th3n_R4M}
```
