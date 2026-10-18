# Web CJK font repair (0.13.0 fork)

The upstream 0.13.0 touch path is user-verified on an actual touchscreen and is unchanged.
This patch repairs Chinese glyph coverage only; language detection, saved preferences,
menu behavior, pointer input and application icons keep their upstream implementation.

The upstream Web build defaults omit the optional CRAFT_FONTS_DIR input. Browser builds
therefore have no installed CJK fonts to use, even though translation catalogs exist.
Download the pinned Noto CJK fonts into an external input directory:

    python3 packaging/web/prepare-fonts.py /absolute/font-input
    CRAFT_FONTS_DIR=/absolute/font-input CRAFT_FONTS_REQUIRED=1 packaging/web/package.sh

The font preparer verifies the fixed upstream commit's SC/TC/JP/KR SHA-256 values and
OFL licenses. No font binaries are committed. The existing Trunk hook copies them into
the final site's content-addressed fonts/ paths. SC is loaded before the first frame;
other faces load in the background. The Web shell registers loaded CJK bytes in egui's
UI families, independently of FontDb for document text, and restores registrations
when font definitions or the graphics context are reset.

The Web workflow compiles and packages on GitHub and uploads a ZIP, SHA256SUMS and
SOURCE.txt. Deployment is separate. Check Chinese menus, Chinese filenames, switching
English/Chinese and persistence after reload. Existing upstream touch behavior must
remain unchanged. A build or HTTP 200 alone is not a browser font acceptance test.
