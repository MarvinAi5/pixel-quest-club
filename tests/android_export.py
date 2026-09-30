"""Disposable debug APK export; no production signing credentials."""
import os,json,subprocess,hashlib,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'qa-artifacts';out.mkdir(exist_ok=True)
settings_dir=Path.home()/'.config/godot';settings_dir.mkdir(parents=True,exist_ok=True)
settings=list(settings_dir.glob('editor_settings-*.tres'));settings_path=settings[0] if settings else settings_dir/'editor_settings-4.7.tres'
sdk=os.environ['ANDROID_HOME'];java=os.environ['JAVA_HOME']
settings_path.write_text('[gd_resource type="EditorSettings" format=3]\n[resource]\nexport/android/android_sdk_path = '+json.dumps(sdk)+'\nexport/android/java_sdk_path = '+json.dumps(java)+'\n')
subprocess.run(['keytool','-genkeypair','-noprompt','-keystore','/tmp/pqc-debug.keystore','-storepass','android','-keypass','android','-alias','androiddebugkey','-keyalg','RSA','-keysize','2048','-validity','10000','-dname','CN=Android Debug,O=Android,C=US'],check=True)
preset='''[preset.0]
name="Android"
platform="Android"
runnable=true
advanced_options=false
dedicated_server=false
export_filter="all_resources"
include_filter=""
exclude_filter="CourseTest.gd,README.txt"
export_path=""
script_export_mode=2
[preset.0.options]
custom_template/debug="/tmp/pqc-templates/templates/android_debug.apk"
gradle_build/use_gradle_build=false
architectures/armeabi-v7a=false
architectures/arm64-v8a=true
architectures/x86=false
architectures/x86_64=false
package/unique_name="club.pixelquest.referenceqa"
package/name="Pixel Quest Reference QA"
package/signed=true
keystore/debug="/tmp/pqc-debug.keystore"
keystore/debug_user="androiddebugkey"
keystore/debug_password="android"
permissions/internet=false
'''
(root/'godot-reference/export_presets.cfg').write_text(preset)
apk=out/'pixel-quest-reference-debug.apk';godot='/tmp/godot/Godot_v4.7.2-stable_linux.x86_64'
r=subprocess.run([godot,'--headless','--path',str(root/'godot-reference'),'--export-debug','Android',str(apk)],capture_output=True,text=True)
(out/'android-export.log').write_text(r.stdout+r.stderr)
if r.returncode:raise RuntimeError('Android export failed; see android-export.log')
assert apk.exists() and apk.stat().st_size>1000000
with zipfile.ZipFile(apk) as z:
 names=z.namelist();assert 'AndroidManifest.xml' in names;assert any(n.startswith('lib/arm64-v8a/') for n in names)
tools=Path(sdk)/'build-tools/35.0.1';subprocess.run([str(tools/'apksigner'),'verify',str(apk)],check=True)
badging=subprocess.check_output([str(tools/'aapt'),'dump','badging',str(apk)],text=True);(out/'android-manifest.txt').write_text(badging)
report=dict(status='passed',godot='4.7.2',architecture='arm64-v8a',bytes=apk.stat().st_size,sha256=hashlib.sha256(apk.read_bytes()).hexdigest(),checks=['Godot debug export succeeded','Android manifest exists','ARM64 engine libraries included','APK signature verified'],limits='Built and checked on CI; not installed or played on physical Retroid. Disposable standard debug key only.')
(out/'android-results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
# Avoid uploading any signing key or temporary preset.
(root/'godot-reference/export_presets.cfg').unlink()
