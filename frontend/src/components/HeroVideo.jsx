import { useEffect, useRef, useState } from 'react'
import { useI18n } from '../i18n/context'
import { PlayIcon, SoundOffIcon, SoundOnIcon } from './Icons'

const VIDEO_SRC = '/videos/snani-intro.mp4'
const POSTER_SRC = '/videos/snani-intro-poster.jpg'

// Autoplays muted and looping (browsers block autoplay with sound). Turning the sound on
// restarts the video from the beginning and stops the loop so it is not heard repeatedly.
export default function HeroVideo() {
  const { t } = useI18n()
  const videoRef = useRef(null)
  const [muted, setMuted] = useState(true)
  const [playing, setPlaying] = useState(false)

  useEffect(() => {
    const video = videoRef.current
    if (!video || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
    video.play().catch(() => {
      // autoplay refused: the play button stays visible
    })
  }, [])

  function play() {
    videoRef.current?.play().catch(() => {})
  }

  function togglePlayback() {
    const video = videoRef.current
    if (!video) return
    if (video.paused) play()
    else video.pause()
  }

  function toggleSound() {
    const video = videoRef.current
    if (!video) return
    const nextMuted = !video.muted
    video.muted = nextMuted
    setMuted(nextMuted)
    if (!nextMuted) {
      video.currentTime = 0
    }
    play()
  }

  return (
    <figure className="hero-video">
      <div className="video-frame">
        <video
          ref={videoRef}
          className="video-el"
          src={VIDEO_SRC}
          poster={POSTER_SRC}
          muted
          loop={muted}
          playsInline
          preload="metadata"
          aria-label={t.hero.videoLabel}
          onClick={togglePlayback}
          onPlay={() => setPlaying(true)}
          onPause={() => setPlaying(false)}
          onEnded={() => setPlaying(false)}
        />

        {!playing ? (
          <button type="button" className="video-play" onClick={play} aria-label={t.hero.videoPlay}>
            <PlayIcon size={34} />
          </button>
        ) : null}

        <button
          type="button"
          className={`video-sound ${muted ? '' : 'is-on'}`}
          onClick={toggleSound}
          aria-pressed={!muted}
        >
          {muted ? <SoundOffIcon size={18} /> : <SoundOnIcon size={18} />}
          <span>{muted ? t.hero.videoSoundOn : t.hero.videoSoundOff}</span>
        </button>
      </div>
      <figcaption className="video-caption">{t.hero.videoCaption}</figcaption>
    </figure>
  )
}
