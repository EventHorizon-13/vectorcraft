"""Reapply this deployment's font, icon and menu fixes to a fixed official release."""
import pathlib,sys,hashlib,urllib.request,shutil,re,json,subprocess
P=pathlib.Path
app=sys.argv[1];root=P(sys.argv[2]).resolve();old=P(sys.argv[3]).resolve()
font_dir=root.parent/'local-font-input';font_dir.mkdir(exist_ok=True)
font_url='https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/1aed5ea2dcf7cb0bf35635f378b2326461ba0df0/data/fonts/'
checks={'DroidSansFallbackFull.ttf':'97320619b0f1ce4a7cda74cf064a0ce44ef3091287bc42755597e177cccf94c2','NOTICE':'38751245389e1e23f73e6f5384b5cbe7fa972cc4410c5adc9c04b082a0b9561a'}
for name,digest in checks.items():
 p=font_dir/name
 if not p.exists():p.write_bytes(urllib.request.urlopen(font_url+name,timeout=90).read())
 assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
ui=root/'crates/ui-egui';build=ui/'build.rs';s=build.read_text();assert s.count('fn main() {')==1
s=s.replace('fn main() {','fn main() {\n    write_local_chinese_font();',1)
s+='''
// Deployment font input is external to this repository and hash-verified by CI.
fn write_local_chinese_font() {
    let source = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../local-font-input/DroidSansFallbackFull.ttf");
    println!("cargo::rerun-if-changed={}", source.display());
    let out = std::path::PathBuf::from(std::env::var_os("OUT_DIR").unwrap()).join("local-chinese.ttf");
    std::fs::copy(source, out).expect("verified external Chinese font");
}
'''
# The input sits beside the upstream checkout: crates/ui-egui -> ../../.. .
build.write_text(s)
module='''//! Deployment Chinese glyph fallback, retained on every font reset.
pub(crate) fn with_chinese(mut fonts: egui::FontDefinitions) -> egui::FontDefinitions {
    let key = "deployment-chinese".to_owned();
    fonts.font_data.insert(key.clone(), std::sync::Arc::new(egui::FontData::from_static(include_bytes!(concat!(env!("OUT_DIR"), "/local-chinese.ttf")))));
    for stack in fonts.families.values_mut() {
        stack.retain(|n| n != &key);
        let at = stack.iter().position(|n| {
            let n = n.to_ascii_lowercase();
            n.contains("craft") || n.contains("gothic") || n.contains("cjk") || n.contains("system-") || n.contains("japanese")
        }).unwrap_or(stack.len());
        stack.insert(at, key.clone());
    }
    fonts
}
'''
(ui/'src/local_chinese.rs').write_text(module)
lib=ui/'src/lib.rs';lib.write_text(lib.read_text()+'\nmod local_chinese;\n')
count=0
for f in (ui/'src').rglob('*.rs'):
 if f.name=='local_chinese.rs':continue
 s=f.read_text();edits=[]
 for match in re.finditer(r'\.set_fonts\(',s):
  start=match.end();depth=1;i=start;quote=False;escaped=False
  while depth:
   c=s[i]
   if quote:
    if escaped:escaped=False
    elif c=='\\':escaped=True
    elif c=='"':quote=False
   elif c=='"':quote=True
   elif c=='(':depth+=1
   elif c==')':depth-=1
   i+=1
  arg=s[start:i-1];assert 'with_chinese' not in arg
  edits.append((start,i-1,'crate::local_chinese::with_chinese('+arg+')'));count+=1
 for a,b,new in reversed(edits):s=s[:a]+new+s[b:]
 if edits:f.write_text(s)
assert count>=1
if app in ['vectorcraft','photocraft','pdfcraft']:
 icon={'vectorcraft':'vc-glass','photocraft':'pc-glass','pdfcraft':'pdf-glass'}[app]
 src=old/'assets/app-icon'/icon;assert src.is_dir();shutil.copytree(src,root/'assets/app-icon'/icon,dirs_exist_ok=True)
 if app!='pdfcraft':
  f=ui/'src/brand.rs';s=f.read_text();s,n=re.subn(r'include_bytes!\("[^"\n]+"\)',f'include_bytes!("../../../assets/app-icon/{icon}/titlebar-128.png")',s,count=1);assert n==1;f.write_text(s)
 else:
  f=ui/'src/widgets.rs';s=f.read_text();previous=(old/'crates/ui-egui/src/widgets.rs').read_text()
  a=previous.index('pub fn artcraft_logo(');b=previous.index('pub fn community_links(',a)
  c=s.index('pub fn artcraft_logo(');d=s.index('pub fn community_links(',c)
  s=s[:c]+previous[a:b]+s[d:];f.write_text(s)
if app=='photocraft':
 appdir=root/'apps/photocraft-web';shutil.copy2(old/'apps/photocraft-web/src/touch_menu.rs',appdir/'src/touch_menu.rs')
 f=appdir/'src/main.rs';f.write_text(f.read_text()+'\n#[cfg(target_arch = "wasm32")]\nmod touch_menu;\n')
 f=appdir/'src/web.rs';s=f.read_text();anchor='        let q = query();';assert anchor in s
 s=s.replace(anchor,'        if let Err(error) = crate::touch_menu::install(&document, &canvas) { log::warn!("touch menu compatibility: {error:?}"); }\n'+anchor,1);f.write_text(s)
 f=appdir/'Cargo.toml';s=f.read_text();s=s.replace('features = ["Window"','features = ["Touch", "TouchList", "TouchEvent", "AddEventListenerOptions", "Window"',1);f.write_text(s)
 f=ui/'src/i18n/system.rs';s=f.read_text();pattern=r'(#\[cfg\(all\(not\(test\), target_arch = "wasm32"\)\)\]\s*fn detect_system_tags\(\) -> Vec<String> \{)\s*Vec::new\(\)'
 s,n=re.subn(pattern,r'\1\n    vec!["zh-CN".to_owned()]',s);assert n==1;f.write_text(s)
if app=='gridcraft':
 f=root/'apps/gridcraft-web/src/web.rs';s=f.read_text();a=s.index('                    // Follow the browser');b=s.index('                    // Preferences from an earlier visit',a)
 s=s[:a]+'                    app.ui.language = gridcraft_ui_egui::i18n::Language::system();\n'+s[b:];f.write_text(s)
out=root/'deployment-font-source.json';out.write_text(json.dumps([{'file':n,'url':font_url+n,'sha256':d} for n,d in checks.items()],indent=2))
print(json.dumps({'app':app,'wrapped_font_resets':count,'font':checks['DroidSansFallbackFull.ttf']}))
