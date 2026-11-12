# تحليل وتوثيق نظام Lineage (血脉) وتشفير العميل في Conquer Online Mobile

## 1. التشفير المستخدم في العميل والسيرفر (Encryption Architecture)

1. **مرحلة تسجيل الدخول (Account Login / Auth):**
   - العميل يستخدم بالفعل تشفير **RSA** عبر المفتاح العمومي (Public Key) المخزن في `tools/keys/` و `tools/mod/og_rsa_modulus.txt`.
   - يتم تشفير اسم المستخدم وكلمة المرور وتوكن المصادقة عبر RSA قبل إرسالها إلى خادم الحسابات (Account Server / SDK).
2. **مرحلة حزم اللعب (Game World Traffic - Ports 8020 / 5816):**
   - بعد نجاح تسجيل الدخول، يتم تشفير الحزم باستخدام خوارزمية **CAST5 / Blowfish في وضع CFB64** (`CAST_cfb64_encrypt` كما في العنوان `0x1733d6c`).
   - داخل الحزمة بعد فك تشفيرها، يتم استخدام **Google Protocol Buffers (Protobuf)** لتمثيل الحقول (مثل `CMsgAction`, `CMsgXueMai`, إلخ).

---

## 2. كيفية فتح وعرض نوافذ الـ Lineage (血脉) داخل كود العميل C++

من خلال تحليل مكتبة العميل الأصلية `libCQ2ClientEn.so`:

### أ. الدالة الرئيسية المسؤولة عن فتح الـ Lineage:
الدالة الأصلية المسؤولة عن فتح واجهات الـ Lineage هي:
`CSubProfMrg::OpenProfMain()` (العنوان: `0x00e7ba4c`).

**الكود المفكك (Disassembly) لـ `OpenProfMain`:**
```cpp
uint slots = CSubProfMrg::GetProfSlot(hero->GetProfession());
if (slots <= 2) {
    // إذا لم يفتح اللاعب أكثر من فتحتين
    PostCmd(0xdd4, 0xc95); // يفتح نافذة 3221 (CDlgProfOpen - نافذة التفعيل الأولية)
} else {
    // إذا كان اللاعب قد فتح أكثر من خانتين
    if (HasGroup()) {
        PostCmd(0xdd4, 0xc9f); // يفتح نافذة 3231 (CDlgProfView)
    } else {
        PostCmd(0xdd4, 0xc95); // يفتح 3221 (CDlgProfOpen)
        PostCmd(0xdd4, 0xca0); // ويفتح 3232 (CDlgProfGroup)
    }
}
```

### ب. معنى الأوامر الداخلية في محرك اللعبة (Engine GUI Commands):
- **`PostCmd(0xdd4, dlg_id)`** حيث `0xdd4 = 3540`: هو أمر **فتح النافذة (Open Window)**.
- **`PostCmd(0xcf0, dlg_id)`** حيث `0xcf0 = 3312`: هو أمر **تحديث محتوى النافذة (Refresh Window)**.
- **`PostCmd(0xcf6, dlg_id)`** حيث `0xcf6 = 3318`: هو أمر **إغلاق النافذة (Close Window)**.

### ج. أرقام النوافذ (Dialog IDs) الخاصة بنظام الـ Lineage:
- **`3221` (`0xc95`)**: `CDlgProfOpen` (واجهة تفعيل وفتح الـ Lineage لأول مرة).
- **`3222` (`0xc96`)**: `CDlgProfUpgrade` (واجهة ترقية وتطوير الـ Lineage).
- **`3223` (`0xc97`)**: `CDlgProfInherit` (واجهة توريث الـ Lineage).
- **`3224` (`0xc98`)**: `CDlgProfSlot` (واجهة اختيار وتثبيت خانات الـ Lineage).
- **`3225` (`0xc99`)**: `CDlgProfInheritConfirm` (واجهة تأكيد التوريث).
- **`3231` (`0xc9f`)**: `CDlgProfView` (واجهة عرض خطط ومجموعات الـ Lineage).
- **`3232` (`0xca0`)**: `CDlgProfGroup` (واجهة إدارة مجموعات الـ Lineage).

---

## 3. لماذا لم يعمل أمر `/lineage_show` المباشر؟
1. الأمر السابق كان يرسل حزمة `CMsgAction` (الرقم `0x273e`) برقم أكشن `258` ونص `Lua_OpenWindow|3223,0`.
2. من خلال فحص كود الأكشن `258` في العميل، هذا الأكشن **لا ينفذ دوال Lua العشوائية**، بل يستمع فقط لأحداث وسيناريوهات محددة (مثل المهام السينمائية `ClientTaskTemplate` وتأثير الطيران للجوائز `ClientFlyItemToHero_Open`).
3. نوافذ `CDlgProfOpen` و `CDlgProfUpgrade` ليست FairyGUI Lua Windows بل هي C++ Classes مبنية داخل المحرك ويتم فتحها داخلياً عبر الضغط على الزر المخصص لها أو عبر أمر المحرك الداخلي.

---

## 4. كيفية ظهور زر الـ Lineage في القائمة الجانبية (HUD 1809)

في واجهة القائمة الجانبية للشاشة (`ini/gui/1809.ini`):
- زر الـ Lineage هو:
  ```ini
  [1809-1020]
  AniSection=xuemai_xmrkbtn
  text=STR_ZHUJIEMIAN_XUEMAI
  BindFuncID=9
  ```
- يتحكم في ظهور هذا الزر مدير الوظائف `CNewFunctionOpenMgr` وفق نظام شروط فتح الميزات (`NewFuncOpenCfg`):
  - المفتاح: `BindFuncID = 9`.
  - الشروط المقروءة من إعدادات اللعبة (`ini/newfuncopen.lua` / `newfuncopen.dat`):
    - `enable_lev`: المستوى المطلوب.
    - `enable_pro`: المتطلب الاحترافي (Reborn).
    - `server_func` / `condition`.
- عند تحقق الشروط واستلام حزمة `CMsgXueMai` (`0x28a1`) مع `unAction = 2`:
  - العميل ينفذ `PostCmd(0xcf0, 0x711)` مما يقوم بتحديث القائمة 1809 (`CDlgNewMenu::OnRefreshWindow()` -> `CDlgNewMenu::ResetBtnsPos()`).
  - عند ضغط اللاعب على زر `[1809-1020]`، يستدعي العميل تلقائياً `CSubProfMrg::OpenProfMain()` التي تفتح واجهة الـ Lineage المناسبة لحالة الشخصية.

---

## 5. السبب الجذري لعدم ظهور زر الـ Lineage (تحليل جديد)

بعد فك تشفير ملفات `.dat` (`CMyEncryptFile::Decrypt` باستخدام `srand(0x2537)` وفق LCG الخاص بـ `msvcrt` ثم XOR وتدوير بتات ROR بمقدار `i & 7`) وتحليل `CDlgNewMenu::ResetBtnsPos()` (`0x011f6b34`) و `CNewFunctionOpenMgr::ProcessFuncStatus()` (`0x015a3614`):

1. **شروط فتح الزر في `newfuncopen.dat` (`E_FUNC_METE = 9`):**
   - `server_func = 9` (البت رقم 8: `1 << 8 = 0x100` في حزمة `0x273e` أكشن `471` / `0x1d7` حقل `N64Data` رقم 5).
   - `enable_lev = 130`، `enable_task = 7669`.
   - طالما أن البت `0x100` مرفوع في `N64Data` (`FORGE_FUNC_FLAG = 0x7fff_ffff_ffff_ffff`)، فإن دالة `NewFuncOpenCfg_TestEnableCondition` تعيد `true` وتتجاوز شرط الـ Level و الـ Task.

2. **لماذا بقي زر `[1809-1020]` مخفياً رغم إرسال `forge_open`؟**
   - في `ini/gui/1809.ini`، إحداثيات زر `[1809-1020]` الافتراضية هي **`x=10150`** (خارج الشاشة تماماً)، بعكس زر Forge (`[1809-1000]`) الموجود أصلاً على إحداثي `x=150`.
   - لنقل زر `[1809-1020]` من `x=10150` إلى داخل الشبكة (`x=0, y=0`)، يجب تنفيذ `CDlgNewMenu::ResetBtnsPos()` (`PostCmd(0xcf0, 0x711)`) **بعد** أن يقوم `CNewFunctionOpenMgr::SetFunctionFlag` بفك قفل `BindFuncID = 9`.
   - في الكود السابق، كانت `ready()` ترسل `send_lineage_refresh` قبل انتهاء شاشة التحميل (`m_bInitStatus == 0`)، وعندما يعيد `forge_tick()` الإرسال بعد 5 ثوانٍ، يتخطى `ProcessFuncStatus` إرسال `PostCmd(0xcf0, 0x711)` لأن الحالة السابقة كانت `0` (`cbz r1, #0x15a3794`)، فيبقى الزر عالقاً عند `x=10150`!

3. **الإصلاح المطبق:**
   - تعديل `forge_tick()` في `rust/src/world/forge.rs` ليرسل `self.send_lineage_refresh(cid)` مباشرة بعد `self.forge_open(cid)` لشخصيات الـ Reborn.
   - تعديل أمر `/lineage_show` في `rust/src/world/gm.rs` ليستدعي `self.forge_open(cid)` قبل `self.send_lineage_refresh(cid)` لفك القفل وتحديث مواقع أزرار القائمة `1809` فوراً.

---

## 6. القفل الخفي في شاشة التحميل: حزمة `CMsgMBAction` رقم `251` (`0xFB`) و `m_bInitStatus`

بعد ملاحظة عدم ظهور أي زر محكوم بـ `BindFuncID` (مثل `Forge = 6` و `Lineage = 9` وبقية الأزرار، وبقاء 6 أزرار فقط غير مقيدة: `Outfit, Status, Anima, Bag, Skills, Rank`)، أظهر تفكيك `CNewFunctionOpenMgr::ProcessFuncStatus` (`0x015a3614`) و `CFDlgLoading::DoStateChange` (`0x0125e480`) و `CMsgMBAction::Process` السبب الجذري التالي:

1. **التحقق المبكر داخل `CNewFunctionOpenMgr::ProcessFuncStatus` (`0x015a362e`):**
   - أول شرط في الدالة يقرأ الحقل `[this + 0x18]` (`m_bInitStatus`).
   - إذا كان `m_bInitStatus == 0`، تخرج الدالة فوراً (`beq #0x15a3814`) وتصبح كل استدعاءات `SetFunctionFlag` (الأكشن `471` / `0x1d7`) بلا تأثير على حالة الأزرار.

2. **من يقوم بتفعيل `SetInitStatus(true)`؟**
   - الجهة الوحيدة في العميل التي تستدعي `CNewFunctionOpenMgr::SetInitStatus(true)` هي `CFDlgLoading::DoStateChange()` عند العنوان `0x0125e706` (بعد وصول التقدم `[dlg + 0x280] >= 0x400`).
   - لكن قبل ذلك مباشرة (`0x0125e69c`)، تستدعي `CMobileSDKData::IsLoginServerOver()`. وإذا أعادت `false` (`0`)، تقفز لنهاية الدالة (`0x0125e6a2: beq #0x125e730`) ولا تستدعي `SetInitStatus(true)` أبداً!

3. **لماذا كانت تسقط حزمة `login_server_over` (الأكشن 251)؟**
   - في `CMsgMBAction::Process`:
     - عند `0x00f6de0e`: يستدعي `CGamePlayerSet::GetPlayer(idUser, true)`.
     - عند `0x00f6de1e`: يفحص `cmp r0, #0 ; beq #0xf6dfd8`. إذا لم تكن الشخصية موجودة في `CGamePlayerSet`، يتم تجاهل وإسقاط الحزمة فوراً!
     - في مرحلة `login()`، لم تكن حزم `enter()` (التي تنشئ الشخصية في الخريطة) قد أُرسلت بعد، فكان استدعاء `GetPlayer` يعيد `NULL` وتُسقط الحزمة تماماً، مما يمنع ضبط `SetLoginServerOver(true)`.

4. **فخ الإطار 54 في `t.enter` (`action=471, N64Data=0`):**
   - أثناء مرحلة دخول الخريطة `enter()`، كان الخادم يعيد إرسال قوالب الدخول الرسمية والتي تحتوي في الإطار 54 على أكشن 471 مع `N64Data = 0`.
   - هذا كان يعيد تصفير `m_nFunctionFlag` إلى `0` ويقفل جميع الميزات.
   - بالإضافة إلى ذلك، في `CNewFunctionOpenMgr::SetFunctionFlag` (`0x015a3bc4`)، يوجد فحص طرح `subs/sbcs` يقفز ويتخطى حفظ القيمة الجديدة إذا لم تكن سالبة (`-1`).

5. **طبيعة قائمة الـ HUD وأيقونة السهم `∨` / `^` (`[1-2002]`):**
   - أيقونة السهم `∨` في الواجهة الرئيسية هي العنصر `[1-2002]` (`AniSection=menubtn` في `1.ini`).
   - الضغط عليها هو حركة واجهة رسومية محلية (Client-Side GUI Animation) لطي/فتح نافذة `CDlgNewMenu` (النافذة `1809`). ولا تحتاج إلى حزمة خاصة من السيرفر عند الضغط.
   - عند فتحها، تعرض الأزرار التي قامت دالة `CDlgNewMenu::ResetBtnsPos` بوضعها في شبكة الأعمدة (4 أزرار لكل عمود `LineNum = 4`).
   - لأن الأزرار المقفلة تعيد `IsWindowVisible() == false`، فإنها تُستبعد تماماً من الشبكة، ولهذا كان يظهر فقط 6 أزرار (4 في العمود الأول و 2 في العمود الثاني).

6. **الحل الشامل والمطبق في السيرفر:**
   - **تصفية الإطار 54 من `t.enter`**: منع إرسال أكشن 471 بقيمة 0.
   - **إرسال `login_server_over` و `forge_open` فور إنشاء الشخصية في `enter()`**: حيث تكون الشخصية موجودة في `CGamePlayerSet` فتنجح المعالجة وتُفعل `SetInitStatus(true)`.
   - **إعادة إرسال `login_server_over` و `forge_open` في `ready()` و `forge_tick` و `/lineage_show`**: لضمان استمرار فك القفل وتحديث مواقع أزرار `1809`.


