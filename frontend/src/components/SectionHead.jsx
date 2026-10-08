export default function SectionHead({ eyebrow, title, lead, center = false }) {
  return (
    <div className={`section-head ${center ? 'is-center' : ''}`}>
      <span className="eyebrow">{eyebrow}</span>
      <h2>{title}</h2>
      {lead ? <p className="lead">{lead}</p> : null}
    </div>
  )
}
