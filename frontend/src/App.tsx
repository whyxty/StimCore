import { useState } from 'react';
import { T } from './theme';
import { Dot } from './components/atoms';
import { ScreenConfig } from './screens/ScreenConfig';
import { ScreenInputs } from './screens/ScreenInputs';
import { ScreenResults } from './screens/ScreenResults';
import { ScreenTaskDetail } from './screens/ScreenTaskDetail';
import { DEFAULT_INPUTS, type Inputs, type ScreenId } from './store';
import { calcAll } from './api';

export default function App() {
  const [screen, setScreen] = useState<ScreenId>('config');
  const [selectedTask, setSelectedTask] = useState<string | null>(null);
  const [inputs, setInputs] = useState<Inputs>(DEFAULT_INPUTS);
  const [results, setResults] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState<string | null>(null);

  async function handleCalculate() {
    setLoading(true); setError(null);
    try {
      const r = await calcAll(inputs as unknown as Record<string, unknown>);
      setResults(r);
      setScreen('results');
      setSelectedTask(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  function openTask(id: string) {
    setSelectedTask(id);
    setScreen('task');
  }

  return (
    <div style={{
      width: '100%', height: '100%', display: 'flex',
      background:
        'radial-gradient(circle at 0% 0%, rgba(0,229,255,0.04) 0%, transparent 40%),' +
        'radial-gradient(circle at 100% 100%, rgba(167,139,250,0.03) 0%, transparent 40%),' +
        T.bg0,
      color: T.text0,
    }}>
      <Sidebar screen={screen} setScreen={setScreen} />
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <Header />
        <div style={{ flex: 1, overflow: 'auto' }}>
          {error && (
            <div style={{
              margin: 16, padding: '10px 14px', borderRadius: 6,
              background: T.red + '14', border: `1px solid ${T.red}55`,
              color: T.red, fontFamily: T.mono, fontSize: 12,
            }}>
              {error}
            </div>
          )}
          {screen === 'config'  && <ScreenConfig />}
          {screen === 'inputs'  && (
            <ScreenInputs
              inputs={inputs} setInputs={setInputs}
              onCalculate={handleCalculate} loading={loading}
            />
          )}
          {screen === 'results' && (
            <ScreenResults results={results} onOpenTask={openTask} />
          )}
          {screen === 'task' && selectedTask && (
            <ScreenTaskDetail
              taskId={selectedTask}
              results={results}
              onBack={() => setScreen('results')}
              onOpenTask={openTask}
            />
          )}
        </div>
      </main>
    </div>
  );
}

// ─── Sidebar ──────────────────────────────────────────────────────
function Sidebar({ screen, setScreen }: { screen: ScreenId; setScreen: (s: ScreenId) => void }) {
  const items: { id: ScreenId; label: string; sub: string }[] = [
    { id: 'config',  label: 'Настройки месторождения', sub: 'Константы профиля' },
    { id: 'inputs',  label: 'Исходные данные',         sub: 'Параметры скважины' },
    { id: 'results', label: 'Расчёты',                  sub: '12 задач СКО' },
  ];
  return (
    <aside style={{
      width: 240, background: T.bg1, borderRight: `1px solid ${T.border}`,
      padding: '20px 16px', display: 'flex', flexDirection: 'column', gap: 18,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <Dot color={T.accent} size={9} pulse />
        <span style={{
          fontFamily: T.sans, fontSize: 18, fontWeight: 700,
          color: T.text0, letterSpacing: '-0.02em',
        }}>StimCore</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        {items.map((it, i) => {
          const active = screen === it.id;
          return (
            <button key={it.id} onClick={() => setScreen(it.id)} style={{
              textAlign: 'left', cursor: 'pointer',
              background: active ? T.bg2 : 'transparent',
              border: `1px solid ${active ? T.accent + '55' : 'transparent'}`,
              borderRadius: 6, padding: '10px 12px',
              transition: 'all .15s',
            }}>
              <div style={{
                fontFamily: T.mono, fontSize: 9, fontWeight: 700,
                color: active ? T.accent : T.text3, letterSpacing: '0.16em', marginBottom: 3,
              }}>{`0${i + 1}`}</div>
              <div style={{
                fontSize: 12, fontWeight: active ? 600 : 500,
                color: active ? T.text0 : T.text1, lineHeight: 1.3,
              }}>{it.label}</div>
              <div style={{ fontFamily: T.mono, fontSize: 9, color: T.text3, marginTop: 2 }}>{it.sub}</div>
            </button>
          );
        })}
      </div>

      <div style={{ marginTop: 'auto', borderTop: `1px solid ${T.border}`, paddingTop: 12 }}>
        <div style={{ fontFamily: T.mono, fontSize: 9, color: T.text3, letterSpacing: '0.14em' }}>
          v0.1 · stimcore<br />react+vite · python+fastapi
        </div>
      </div>
    </aside>
  );
}

// ─── Header ───────────────────────────────────────────────────────
function Header() {
  return (
    <header style={{
      borderBottom: `1px solid ${T.border}`,
      padding: '14px 28px',
      background: 'linear-gradient(180deg, ' + T.bg1 + ' 0%, ' + T.bg0 + ' 100%)',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    }}>
      <div>
        <div style={{ fontSize: 16, fontWeight: 700, color: T.text0, letterSpacing: '-0.02em' }}>
          Расчёт солянокислотной обработки
        </div>
        <div style={{ fontFamily: T.mono, fontSize: 11, color: T.text2, marginTop: 2 }}>
          Приложение В · ветка СКО · 12 задач
        </div>
      </div>
      <div style={{
        fontFamily: T.mono, fontSize: 10, color: T.text3,
        letterSpacing: '0.14em', textTransform: 'uppercase',
      }}>
        backend · localhost:8000
      </div>
    </header>
  );
}
