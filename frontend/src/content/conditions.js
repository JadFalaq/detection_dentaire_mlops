export const URGENCY_RANK = { high: 3, medium: 2, low: 1, info: 0 }

export const CONDITIONS = [
  {
    id: 'PERIAPICAL_PATHOLOGY',
    color: '#ff3d7f',
    urgency: 'high',
    fr: {
      name: 'Infection au bout de la racine',
      short: 'Lésion périapicale',
      explain:
        "Une infection ou une inflammation qui se forme sous la dent, au bout de la racine, souvent après une carie profonde non soignée. Sur la radio, elle ressemble à une petite tache sombre au bout de la racine. Elle peut rester sans douleur longtemps, puis se transformer en abcès.",
      advice:
        "Consultez un dentiste rapidement. Sans traitement, l'infection peut s'étendre. En cas de gonflement ou de fièvre, n'attendez pas.",
    },
    ar: {
      name: 'التهاب في طرف الجذر',
      short: 'آفة حول ذروة الجذر',
      explain:
        'التهاب أو عدوى تتكوّن تحت السن في طرف الجذر، غالباً بعد تسوّس عميق لم يُعالَج. في الراديو تظهر كبقعة داكنة صغيرة في نهاية الجذر. قد تبقى بدون ألم لمدة طويلة، ثم تتحوّل إلى خرّاج.',
      advice:
        'استشر طبيب الأسنان بسرعة. بدون علاج قد تنتشر العدوى. في حالة انتفاخ أو حمّى، لا تنتظر.',
    },
  },
  {
    id: 'CARIES',
    color: '#ff7a45',
    urgency: 'medium',
    fr: {
      name: 'Carie',
      short: 'Un « trou » dans la dent',
      explain:
        "Les bactéries attaquent l'émail et creusent la dent. Sur la radio, une carie apparaît comme une zone plus sombre dans la dent. Au début elle ne fait pas mal, puis elle peut devenir douloureuse.",
      advice:
        'Prenez rendez-vous dans les prochaines semaines. Une carie soignée tôt, c’est un simple plombage : moins cher et sans douleur.',
    },
    ar: {
      name: 'تسوّس',
      short: '"ثقب" في السن',
      explain:
        'تهاجم البكتيريا مينا السن وتحفر فيه. في الراديو يظهر التسوّس كمنطقة أغمق داخل السن. في البداية لا يسبّب ألماً، ثم قد يصبح مؤلماً.',
      advice:
        'احجز موعداً خلال الأسابيع القادمة. علاج التسوّس مبكراً يعني حشوة بسيطة، أقل تكلفة وبدون ألم.',
    },
  },
  {
    id: 'PERIODONTAL_BONE',
    color: '#f5b82e',
    urgency: 'medium',
    fr: {
      name: 'Perte d’os autour des dents',
      short: 'Maladie des gencives (parodontite)',
      explain:
        "L'os qui tient les dents diminue, souvent à cause d'une inflammation des gencives qui dure. Signes possibles : gencives qui saignent, mauvaise haleine, dents qui bougent. Sur la radio, l'os est plus bas que la normale.",
      advice:
        'Faites vérifier par un dentiste. Un détartrage et un bon brossage peuvent stopper l’évolution.',
    },
    ar: {
      name: 'فقدان العظم حول الأسنان',
      short: 'مرض اللثة',
      explain:
        'يتراجع العظم الذي يثبّت الأسنان، غالباً بسبب التهاب مزمن في اللثة. من العلامات: نزيف اللثة، رائحة الفم، وتحرّك الأسنان. في الراديو يكون مستوى العظم أقل من الطبيعي.',
      advice:
        'اطلب فحصاً عند طبيب الأسنان. إزالة الجير وتنظيف الأسنان جيداً يمكن أن يوقفا تطوّر المرض.',
    },
  },
  {
    id: 'ROOT_PATHOLOGY',
    color: '#22d3ee',
    urgency: 'medium',
    fr: {
      name: 'Problème de racine',
      short: 'Reste de racine ou racine abîmée',
      explain:
        "Deux situations possibles : un morceau de racine resté dans l'os (par exemple après une dent cassée ou une extraction incomplète), ou une racine qui se « résorbe », c'est-à-dire qui s'use petit à petit.",
      advice:
        'Faites vérifier par un dentiste dans les prochaines semaines. Un reste de racine peut s’infecter avec le temps.',
    },
    ar: {
      name: 'مشكل في الجذر',
      short: 'بقايا جذر أو جذر متضرّر',
      explain:
        'حالتان ممكنتان: بقايا جذر بقيت داخل العظم (مثلاً بعد كسر سن أو قلع غير كامل)، أو جذر يتآكل شيئاً فشيئاً.',
      advice:
        'اطلب فحصاً عند طبيب الأسنان خلال الأسابيع القادمة. بقايا الجذر قد تلتهب مع الوقت.',
    },
  },
  {
    id: 'IMPACTED_TOOTH',
    color: '#a78bfa',
    urgency: 'low',
    fr: {
      name: 'Dent incluse',
      short: 'Une dent restée coincée dans l’os',
      explain:
        "Une dent qui n'a pas pu sortir complètement, très souvent une dent de sagesse. Elle peut ne poser aucun problème, ou au contraire pousser sur la dent voisine et provoquer douleurs ou infections.",
      advice:
        'Pas d’urgence si vous n’avez pas mal. Parlez-en à votre dentiste lors du prochain contrôle : il dira s’il faut la surveiller ou l’enlever.',
    },
    ar: {
      name: 'سن مطمور',
      short: 'سن بقي محبوساً داخل العظم',
      explain:
        'سن لم يستطع الخروج بالكامل، وغالباً ما يكون ضرس العقل. قد لا يسبّب أي مشكل، أو قد يضغط على السن المجاور ويسبّب ألماً أو التهاباً.',
      advice:
        'لا داعي للاستعجال إذا لم تشعر بألم. تحدّث عنه مع طبيبك في الفحص القادم ليقرّر مراقبته أو قلعه.',
    },
  },
  {
    id: 'TREATED_TOOTH',
    color: '#34d399',
    urgency: 'info',
    fr: {
      name: 'Dent déjà soignée',
      short: 'Plombage, couronne ou dévitalisation',
      explain:
        'Une dent qui a déjà reçu un soin : plombage, couronne, bridge ou traitement de racine (dévitalisation). Ces soins apparaissent très blancs sur la radio car ils sont plus denses que la dent.',
      advice:
        'Rien de spécial à faire. Continuez vos contrôles réguliers pour vérifier que les soins tiennent bien.',
    },
    ar: {
      name: 'سن معالَج',
      short: 'حشوة، تاج أو علاج عصب',
      explain:
        'سن سبق علاجه: حشوة، تاج، جسر أو علاج الجذر (قتل العصب). تظهر هذه العلاجات بيضاء جداً في الراديو لأنها أكثف من السن.',
      advice: 'لا شيء خاص للقيام به. واصل الفحوصات الدورية للتأكد من سلامة العلاجات.',
    },
  },
  {
    id: 'DEVICE_IMPLANT',
    color: '#60a5fa',
    urgency: 'info',
    fr: {
      name: 'Implant ou appareil',
      short: 'Implant, bagues ou matériel chirurgical',
      explain:
        "Un élément artificiel : implant dentaire (une vis qui remplace la racine), appareil d'orthodontie (bagues) ou matériel chirurgical (plaque, vis). Le métal apparaît très blanc sur la radio.",
      advice:
        'Pour information. Si vous ne saviez pas qu’il y en avait un, demandez à votre dentiste.',
    },
    ar: {
      name: 'زرعة أو جهاز',
      short: 'زرعة، تقويم أو أداة جراحية',
      explain:
        'عنصر اصطناعي: زرعة سنية (برغي يعوّض الجذر)، جهاز تقويم الأسنان، أو أداة جراحية (صفيحة، برغي). يظهر المعدن أبيض جداً في الراديو.',
      advice: 'للعلم فقط. إذا لم تكن تعلم بوجوده، اسأل طبيب أسنانك.',
    },
  },
]

const BY_ID = Object.fromEntries(CONDITIONS.map((condition) => [condition.id, condition]))

const FALLBACK = {
  id: 'UNKNOWN',
  color: '#94a3b8',
  urgency: 'info',
  fr: { name: 'Élément repéré', short: '', explain: '', advice: '' },
  ar: { name: 'عنصر تم رصده', short: '', explain: '', advice: '' },
}

export function getCondition(id) {
  return BY_ID[id] || { ...FALLBACK, id }
}
