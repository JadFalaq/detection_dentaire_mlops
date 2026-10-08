import './App.css'
import Analyzer from './components/Analyzer'
import Header from './components/Header'
import Hero from './components/Hero'
import { AiExplained, ConditionsGuide, Faq, FinalCta, Footer, HowItWorks } from './components/InfoSections'
import { useServerStatus } from './hooks/useServerStatus'
import { LangProvider } from './i18n/LangProvider'

function Site() {
  const { status, wake, markActive } = useServerStatus()
  return (
    <>
      <Header status={status} />
      <main>
        <Hero />
        <HowItWorks />
        <Analyzer status={status} onWake={wake} onServerActive={markActive} />
        <ConditionsGuide />
        <AiExplained />
        <Faq />
        <FinalCta />
      </main>
      <Footer />
    </>
  )
}

export default function App() {
  return (
    <LangProvider>
      <Site />
    </LangProvider>
  )
}
