const fr = {
  brandTagline: 'Votre radio dentaire, expliquée simplement',
  langSwitch: 'العربية',
  langSwitchLabel: 'Passer en arabe',
  nav: {
    how: 'Comment ça marche',
    guide: 'Les 7 signes',
    ai: "L'IA expliquée",
    faq: 'Questions',
    cta: 'Analyser ma radio',
  },
  status: {
    sleeping: 'IA en veille',
    checking: 'Connexion…',
    waking: 'Réveil de l’IA…',
    ready: 'IA prête',
    offline: 'IA indisponible',
    demo: 'Mode démo',
  },
  hero: {
    eyebrow: 'Gratuit · Français & العربية',
    titleStart: 'Comprenez votre radio dentaire',
    titleAccent: 'en quelques secondes',
    darija: 'Chouf chnou kayn f snanek',
    lead:
      "Vous avez une radio panoramique de vos dents mais vous ne savez pas la lire ? Snani utilise l'intelligence artificielle pour repérer les signes visibles — caries, infections, dents incluses, soins déjà faits — et vous les explique avec des mots simples.",
    ctaPrimary: 'Analyser ma radio',
    ctaSecondary: 'Essayer avec un exemple',
    trust: ['100 % gratuit', 'Sans inscription', 'Radio non conservée'],
    artLabel: "Illustration : l'IA parcourt une radio panoramique et entoure les zones repérées",
    artChips: [
      { label: 'Carie', detail: 'à faire vérifier' },
      { label: 'Dent incluse', detail: 'à surveiller' },
    ],
  },
  how: {
    eyebrow: 'Simple comme bonjour',
    title: 'Comment ça marche ?',
    steps: [
      {
        title: 'Récupérez votre radio',
        text:
          "La radio panoramique (aussi appelée « panoramique dentaire ») se fait dans un centre de radiologie ou chez certains dentistes. Gardez le fichier, ou prenez le film en photo avec votre téléphone.",
      },
      {
        title: 'Envoyez-la à Snani',
        text:
          "Depuis votre téléphone ou votre ordinateur. L'IA examine toute la mâchoire, dent par dent, en quelques secondes.",
      },
      {
        title: 'Comprenez et agissez',
        text:
          'Chaque signe repéré est entouré sur l’image et expliqué simplement, avec un conseil clair : surveiller, prendre rendez-vous ou consulter vite.',
      },
    ],
  },
  analyzer: {
    eyebrow: 'Analyse',
    title: 'Analysez votre radio',
    lead: 'Votre image est analysée puis supprimée immédiatement. Aucune inscription, aucun compte.',
    dropTitle: 'Déposez votre radio panoramique ici',
    dropHint: 'JPG, PNG, WEBP… depuis votre galerie ou vos fichiers',
    choose: 'Choisir une image',
    camera: 'Prendre en photo',
    example: "Pas de radio sous la main ? Essayez avec un exemple",
    exampleLoading: "Chargement de l'exemple…",
    wrongType: "Ce fichier n'est pas une image. Choisissez une photo ou un fichier JPG / PNG.",
    tipsTitle: 'Conseils pour bien photographier votre radio',
    tips: [
      'Posez le film contre une fenêtre ou un écran blanc bien éclairé.',
      'Tenez le téléphone bien parallèle à la radio.',
      'Évitez le flash et les reflets.',
      "Cadrez toute la mâchoire, d'une oreille à l'autre.",
    ],
    privacy: 'Votre radio est analysée puis effacée. Nous ne gardons rien.',
    fileLabel: 'Radio sélectionnée',
    analyze: "Lancer l'analyse",
    change: 'Changer de radio',
    advanced: 'Options avancées',
    quality: 'Niveau de détail',
    qualityOptions: {
      fast: 'Rapide',
      standard: 'Standard (conseillé)',
      detailed: 'Détaillé (plus lent)',
    },
    sensitivity: 'Sensibilité',
    sensitivityOptions: {
      careful: 'Prudente',
      balanced: 'Équilibrée',
      sensitive: 'Sensible',
    },
    sensitivityHelp: {
      careful: 'Montre seulement les signes très nets.',
      balanced: 'Le meilleur compromis (conseillé).',
      sensitive: 'Montre aussi les signes incertains.',
    },
    brightness: 'Luminosité',
    contrast: 'Contraste',
    resetImage: "Rétablir l'image d'origine",
    steps: ['Envoi sécurisé de la radio', "L'IA examine chaque dent", 'Préparation de vos résultats'],
    wakingNote:
      "L'IA se réveille : la première analyse peut prendre jusqu'à une minute. Les suivantes seront rapides.",
    offlineNote:
      "Le serveur d'analyse ne répond pas pour le moment. Vous pouvez quand même essayer, ou revenir dans quelques minutes.",
    retryConnection: 'Réessayer la connexion',
    errors: {
      network: 'Impossible de joindre le serveur. Vérifiez votre connexion internet, puis réessayez.',
      server:
        "L'analyse n'a pas pu aboutir. Essayez avec une image plus nette, ou réessayez dans un instant.",
    },
    retry: 'Réessayer',
  },
  results: {
    title: 'Vos résultats',
    found: (n) => (n === 0 ? 'Aucun élément repéré' : n === 1 ? '1 élément repéré' : `${n} éléments repérés`),
    verdicts: {
      high: {
        title: 'Consultez un dentiste rapidement',
        text:
          "L'IA a repéré au moins un signe qui mérite un avis professionnel sans tarder, surtout si vous avez mal ou si votre joue gonfle.",
      },
      medium: {
        title: 'Prenez rendez-vous chez votre dentiste',
        text:
          "Des signes à faire vérifier ont été repérés. Ce n'est pas une urgence, mais mieux vaut ne pas attendre plusieurs mois.",
      },
      low: {
        title: "Rien d'urgent repéré",
        text:
          "L'IA a surtout repéré des soins déjà faits ou des éléments à simplement surveiller. Continuez vos contrôles habituels.",
      },
      none: {
        title: "Aucun signe repéré par l'IA",
        text:
          "Bonne nouvelle, mais attention : l'IA peut passer à côté de certains problèmes. Si vous avez mal, consultez quand même un dentiste.",
      },
    },
    urgency: {
      high: 'À consulter vite',
      medium: 'À faire vérifier',
      low: 'À surveiller',
      info: 'Pour information',
    },
    certainty: {
      high: 'Certitude élevée',
      medium: 'Certitude moyenne',
      low: 'Certitude faible',
    },
    times: (n) => `× ${n}`,
    whatToDo: 'Que faire ?',
    tapHint: 'Touchez un signe pour le voir sur la radio.',
    legendHint: 'Afficher ou masquer sur l’image',
    download: "Télécharger l'image annotée",
    share: 'Envoyer à mon dentiste',
    whatsapp: 'Partager Snani sur WhatsApp',
    another: 'Analyser une autre radio',
    findDentist: 'Trouver un dentiste près de moi',
    shareTitle: 'Ma radio dentaire analysée par Snani',
    shareText: 'Voici ma radio dentaire analysée par Snani. Pouvez-vous y jeter un œil ?',
    whatsappText: "J'ai découvert Snani : un site gratuit qui explique les radios dentaires avec l'IA 🦷",
    reportFooter: 'Snani · Aide à la compréhension, ne remplace pas un dentiste',
    disclaimer:
      "Snani est un outil d'aide à la compréhension. Il ne pose pas de diagnostic et ne remplace pas l'examen d'un dentiste.",
    demoNotice: 'Mode démo : ces résultats sont fictifs.',
  },
  guide: {
    eyebrow: 'Le guide',
    title: 'Les 7 signes que Snani sait repérer',
    lead: 'Touchez un signe pour comprendre ce que c’est et ce qu’il faut faire.',
    seeOnXray: 'Sur la radio',
  },
  ai: {
    eyebrow: 'Transparence',
    title: "Comment l'IA lit votre radio ?",
    paragraphs: [
      "Snani utilise un modèle de vision par ordinateur appelé YOLO. Comme un étudiant en dentaire, il a appris en regardant des milliers d'exemples : des radios panoramiques sur lesquelles chaque carie, chaque infection et chaque soin avait été entouré à la main.",
      "Quand vous envoyez votre radio, le modèle la parcourt en entier et dessine un cadre autour de chaque zone qui ressemble à ce qu'il a appris, avec un score de certitude.",
    ],
    stats: [
      { value: '1 375', label: 'radios panoramiques étudiées' },
      { value: '18 568', label: 'éléments annotés à la main' },
      { value: '7', label: 'familles de signes reconnues' },
    ],
    honestyTitle: 'Ce que l’IA fait bien… et moins bien',
    meters: [
      {
        label: 'Quand elle signale quelque chose',
        value: 'elle a raison environ 7 à 9 fois sur 10',
        ratio: 0.78,
        tone: 'good',
      },
      {
        label: 'Parmi tous les problèmes présents',
        value: 'elle en repère environ 4 sur 10',
        ratio: 0.43,
        tone: 'warn',
      },
    ],
    honestyNote:
      "C'est pour cela qu'un résultat sans signe ne veut pas dire que tout va bien. Snani est fait pour vous aider à comprendre votre radio et à poser les bonnes questions à votre dentiste — pas pour le remplacer.",
    source: "Mesuré sur des radios que le modèle n'avait jamais vues, dont certaines venant d'autres cabinets.",
  },
  faq: {
    eyebrow: 'Questions fréquentes',
    title: 'Vous vous demandez…',
    items: [
      {
        q: 'Est-ce que Snani remplace le dentiste ?',
        a: "Non. Snani vous aide à comprendre ce qu'on voit sur votre radio, mais seul un dentiste peut poser un diagnostic, en vous examinant et en connaissant votre histoire.",
      },
      {
        q: 'Comment obtenir une radio panoramique ?',
        a: "Elle est généralement demandée par votre dentiste et réalisée dans un centre de radiologie ou un cabinet équipé. On vous remet un film, un fichier ou un CD. Vous pouvez envoyer le fichier directement, ou prendre le film en photo.",
      },
      {
        q: 'Que devient ma radio ?',
        a: "Elle est envoyée de façon sécurisée, analysée, puis supprimée immédiatement. Pas de compte, pas d'inscription, aucune donnée gardée.",
      },
      {
        q: "C'est vraiment gratuit ?",
        a: 'Oui, entièrement. Snani est un projet étudiant qui a pour but de rendre la santé dentaire plus compréhensible pour tout le monde.',
      },
      {
        q: "L'IA n'a rien trouvé, mais j'ai mal. Pourquoi ?",
        a: "L'IA ne repère qu'une partie des problèmes, et certains ne se voient pas sur une radio. Une douleur est toujours une bonne raison de consulter un dentiste.",
      },
      {
        q: 'Quelles images fonctionnent ?',
        a: "Uniquement les radios panoramiques, qui montrent toute la mâchoire d'un coup. Les petites radios d'une seule dent et les photos de la bouche ne donneront pas de bons résultats.",
      },
    ],
  },
  final: {
    title: 'Prêt à comprendre votre sourire ?',
    text: 'Gratuit, rapide et confidentiel. En français ou en arabe.',
    cta: 'Analyser ma radio',
  },
  footer: {
    urgent:
      'Douleur forte, joue gonflée ou fièvre ? N’attendez pas : consultez un dentiste ou rendez-vous aux urgences.',
    rights: 'Outil d’information — ne constitue pas un avis médical.',
  },
}

export default fr
