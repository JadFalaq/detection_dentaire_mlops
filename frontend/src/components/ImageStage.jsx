import { getCondition } from '../content/conditions'
import { useI18n } from '../i18n/context'

export default function ImageStage({ preview, detections, activeClass, hiddenClasses, analyzing }) {
  const { lang } = useI18n()
  const { url, width, height } = preview

  return (
    <div className={`image-stage ${analyzing ? 'is-analyzing' : ''}`} dir="ltr">
      <div className="image-frame">
        <img src={url} alt="" className="stage-image" />
        {analyzing ? <div className="stage-scan" aria-hidden="true" /> : null}
        {detections
          .filter((detection) => !hiddenClasses.has(detection.class_name))
          .map((detection, index) => {
            const [x1, y1, x2, y2] = detection.bbox_xyxy
            const condition = getCondition(detection.class_name)
            const dimmed = activeClass && activeClass !== detection.class_name
            const highlighted = activeClass === detection.class_name
            return (
              <div
                key={`${detection.class_name}-${index}`}
                className={`bbox ${dimmed ? 'is-dimmed' : ''} ${highlighted ? 'is-active' : ''}`}
                style={{
                  '--box-color': condition.color,
                  left: `${(x1 / width) * 100}%`,
                  top: `${(y1 / height) * 100}%`,
                  width: `${((x2 - x1) / width) * 100}%`,
                  height: `${((y2 - y1) / height) * 100}%`,
                  animationDelay: `${Math.min(index, 12) * 70}ms`,
                }}
              >
                <span className="bbox-tag" dir={lang === 'ar' ? 'rtl' : 'ltr'}>
                  {condition[lang].name}
                </span>
              </div>
            )
          })}
      </div>
    </div>
  )
}
