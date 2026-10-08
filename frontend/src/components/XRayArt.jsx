const TEETH_PER_ROW = 14
const LEFT = 62
const SPAN = 396
const IMPLANT_INDEX = 10
const TREATED_INDEXES = new Set([2, 11])

function toothLayout(index) {
  const t = index / (TEETH_PER_ROW - 1)
  const x = LEFT + t * SPAN
  const smile = Math.cos(Math.PI * (t - 0.5))
  const fromCenter = Math.abs(t - 0.5)
  const width = fromCenter > 0.3 ? 25 : fromCenter > 0.15 ? 21 : 17
  return { x, smile, width }
}

function toothPath(x, occlusal, width, direction) {
  const half = width / 2
  const crown = 28 * direction
  const root = 70 * direction
  const tip = 76 * direction
  return [
    `M ${x - half} ${occlusal - crown}`,
    `L ${x - half} ${occlusal - 6 * direction}`,
    `Q ${x - half} ${occlusal} ${x - half + 6} ${occlusal}`,
    `L ${x + half - 6} ${occlusal}`,
    `Q ${x + half} ${occlusal} ${x + half} ${occlusal - 6 * direction}`,
    `L ${x + half} ${occlusal - crown}`,
    `L ${x + half - 3} ${occlusal - root}`,
    `Q ${x} ${occlusal - tip} ${x - half + 3} ${occlusal - root}`,
    'Z',
  ].join(' ')
}

const UPPER = Array.from({ length: TEETH_PER_ROW }, (_, index) => {
  const { x, smile, width } = toothLayout(index)
  const occlusal = 136 + 20 * smile
  return { index, x, width, occlusal, d: toothPath(x, occlusal, width, 1) }
})

const LOWER = Array.from({ length: TEETH_PER_ROW }, (_, index) => {
  const { x, smile, width } = toothLayout(index)
  const occlusal = 148 + 20 * smile
  return { index, x, width, occlusal, d: toothPath(x, occlusal, width, -1) }
})

const implant = LOWER[IMPLANT_INDEX]
const caries = UPPER[4]
const periapical = LOWER[3]

const DETECTIONS = [
  { key: 'caries', color: '#ff7a45', x: caries.x - 15, y: caries.occlusal - 32, w: 30, h: 34, label: 'CARIES' },
  {
    key: 'periapical',
    color: '#ff3d7f',
    x: periapical.x - 18,
    y: periapical.occlusal + 48,
    w: 36,
    h: 38,
    label: 'INFECTION',
  },
  { key: 'impacted', color: '#a78bfa', x: 456, y: 168, w: 52, h: 46, label: 'INCLUSE' },
  { key: 'implant', color: '#60a5fa', x: implant.x - 16, y: implant.occlusal - 4, w: 32, h: 82, label: 'IMPLANT' },
]

export default function XRayArt({ label }) {
  return (
    <svg className="xray-art" viewBox="0 0 520 300" role="img" aria-label={label}>
      <defs>
        <radialGradient id="xr-bg" cx="50%" cy="45%" r="70%">
          <stop offset="0%" stopColor="#3a4258" />
          <stop offset="55%" stopColor="#1a1f2e" />
          <stop offset="100%" stopColor="#0b0e17" />
        </radialGradient>
        <linearGradient id="xr-tooth" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#f4f6fb" stopOpacity="0.92" />
          <stop offset="100%" stopColor="#c9d1e3" stopOpacity="0.55" />
        </linearGradient>
        <linearGradient id="xr-scan" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#7c8cff" stopOpacity="0" />
          <stop offset="70%" stopColor="#7c8cff" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#c7d0ff" stopOpacity="0.95" />
        </linearGradient>
        <filter id="xr-blur" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="6" />
        </filter>
      </defs>

      <rect width="520" height="300" rx="22" fill="url(#xr-bg)" />

      <g opacity="0.16" fill="#dfe6f7" filter="url(#xr-blur)">
        <path d="M30 70 Q260 20 490 70 L490 130 Q260 175 30 130 Z" />
        <path d="M40 175 Q260 225 480 175 L470 260 Q260 300 50 260 Z" />
      </g>

      <g className="xr-teeth">
        {UPPER.map((tooth) => (
          <path
            key={`u${tooth.index}`}
            d={tooth.d}
            fill="url(#xr-tooth)"
            opacity={TREATED_INDEXES.has(tooth.index) ? 1 : 0.82}
          />
        ))}
        {LOWER.map((tooth) =>
          tooth.index === IMPLANT_INDEX ? (
            <g key="implant">
              <rect x={tooth.x - 9} y={tooth.occlusal} width="18" height="20" rx="5" fill="#ffffff" />
              <rect x={tooth.x - 5} y={tooth.occlusal + 22} width="10" height="50" rx="3" fill="#f1f5ff" />
              {[30, 40, 50, 60].map((offset) => (
                <line
                  key={offset}
                  x1={tooth.x - 7}
                  x2={tooth.x + 7}
                  y1={tooth.occlusal + offset}
                  y2={tooth.occlusal + offset + 3}
                  stroke="#9aa6c4"
                  strokeWidth="1.5"
                />
              ))}
            </g>
          ) : (
            <path
              key={`l${tooth.index}`}
              d={tooth.d}
              fill="url(#xr-tooth)"
              opacity={TREATED_INDEXES.has(tooth.index) ? 1 : 0.82}
            />
          ),
        )}
        <path
          d={toothPath(482, 196, 26, -1)}
          transform="rotate(-48 482 196)"
          fill="url(#xr-tooth)"
          opacity="0.8"
        />
        <ellipse cx={caries.x + 2} cy={caries.occlusal - 14} rx="5" ry="6" fill="#141826" opacity="0.75" />
        <ellipse cx={periapical.x} cy={periapical.occlusal + 70} rx="9" ry="8" fill="#0f1220" opacity="0.7" />
      </g>

      <g className="xr-detections">
        {DETECTIONS.map((box, order) => (
          <g key={box.key} className="xr-box" style={{ animationDelay: `${0.6 + order * 0.55}s` }}>
            <rect x={box.x} y={box.y} width={box.w} height={box.h} rx="6" fill="none" stroke={box.color} strokeWidth="2.4" />
            <rect x={box.x} y={box.y - 15} width={box.label.length * 6.4 + 10} height="13" rx="4" fill={box.color} />
            <text x={box.x + 5} y={box.y - 5.5} fontSize="9" fontWeight="800" fill="#0b1020" letterSpacing="0.4">
              {box.label}
            </text>
          </g>
        ))}
      </g>

      <rect className="xr-scan" x="-60" y="10" width="60" height="280" fill="url(#xr-scan)" />
    </svg>
  )
}
