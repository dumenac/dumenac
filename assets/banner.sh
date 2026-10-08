#!/usr/bin/env bash
# Renders assets/banner-light.png and assets/banner-dark.png (2560×800, shown at 1280×400) in
# mele.dev's palette. Type is Inter / Inter Display (SIL Open Font License).
#   ./assets/banner.sh
set -euo pipefail
cd "$(dirname "$0")"
DISPLAY_FONT=$(fc-match -f '%{file}' 'Inter Display:style=SemiBold')
SUB_FONT=$(fc-match -f '%{file}' 'Inter Display:style=Regular')
UI_FONT=$(fc-match -f '%{file}' 'Inter:style=Medium')

render() {   # name bg text secondary tertiary link hairline exponential-logo
    local name=$1 bg=$2 fg=$3 sec=$4 ter=$5 link=$6 hair=$7 xlogo=$8 t
    t=$(mktemp -d)
    # shellcheck disable=SC1112  # the curly apostrophe is deliberate typography
    magick -background none -fill "$fg" -font "$DISPLAY_FONT" -pointsize 148 label:'Hi, I’m Domenec Mele' "$t/h1.png"
    magick -background none -fill "$link" -font "$DISPLAY_FONT" -pointsize 148 label:'.' "$t/h2.png"
    magick "$t/h1.png" "$t/h2.png" +append "$t/head.png"
    magick -background none -fill "$sec" -font "$SUB_FONT" -pointsize 62 \
        label:'Startup operator. Product, tech & go-to-market.' "$t/sub.png"
    # bottom row: where I am / was
    lab() { magick -background none -fill "$2" -font "$UI_FONT" -pointsize 36 label:"$1" "$t/$3.png"; }
    logo() { magick "logos/$1.png" -resize 42x42 -background none -gravity center -extent 54x42 "$t/$2.png"; }
    gap() { magick -size "$1"x42 xc:none "$t/$2.png"; }
    lab 'Now' "$ter" l0; gap 18 g0; logo crossmint.com c; lab ' Crossmint' "$fg" l1; gap 52 g1
    lab 'Before' "$ter" l2; gap 18 g2; logo deliveroo.com d; lab ' Deliveroo' "$fg" l3; gap 26 g3
    logo rappi.com r; lab ' Rappi' "$fg" l4; gap 52 g4
    lab 'On the side' "$ter" l5; gap 18 g5; logo "$xlogo" e; lab ' Exponential' "$fg" l6; gap 26 g6
    logo hackspain.com h; lab ' HackSpain' "$fg" l7
    magick -background none -gravity center "$t"/{l0,g0,c,l1,g1,l2,g2,d,l3,g3,r,l4,g4,l5,g5,e,l6,g6,h,l7}.png +append "$t/row.png"
    magick -size 2560x800 xc:none -fill "$bg" -stroke "$hair" -strokewidth 2 \
        -draw "roundrectangle 1,1 2558,798 48,48" \
        "$t/head.png" -geometry +122+150 -composite \
        "$t/sub.png"  -geometry +128+350 -composite \
        -stroke none -fill "$hair" -draw "rectangle 132,556 2428,557" \
        "$t/row.png"  -geometry +128+612 -composite \
        -strip "banner-$name.png"
    rm -rf "$t"
}
render light '#fbfbfd' '#1d1d1f' '#6e6e73' '#86868b' '#0066cc' '#0000001a' goexponential.org-ink
render dark  '#000000' '#f5f5f7' '#a1a1a6' '#86868b' '#2997ff' '#ffffff1f' goexponential.org
echo "✓ banner-light.png, banner-dark.png"
