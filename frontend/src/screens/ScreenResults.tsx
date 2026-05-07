import type { ReactNode } from 'react';
import { T } from '../theme';
import { Card, CardHeader, Tag, Dot } from '../components/atoms';

interface Props {
  results: Record<string, unknown> | null;
  onOpenTask: (id: string) => void;
}

type TaskRes = Record<string, unknown>;

const TASKS: { id: string; title: string; subtitle: string }[] = [
  { id: 'v1',  title: 'В.1',  subtitle: 'Выбор скважины (полная инф.)' },
  { id: 'v2',  title: 'В.2',  subtitle: 'Выбор скважины (огранич.)' },
  { id: 'v3',  title: 'В.3',  subtitle: 'Расход и давление закачки' },
  { id: 'v4',  title: 'В.4',  subtitle: 'Длительность реакции СКР' },
  { id: 'v5',  title: 'В.5',  subtitle: 'Зона растворения' },
  { id: 'v6',  title: 'В.6',  subtitle: 'Растворённая порода (по составу)' },
  { id: 'v7',  title: 'В.7',  subtitle: 'Изменение пористости' },
  { id: 'v8',  title: 'В.8',  subtitle: 'Проницаемость' },
  { id: 'v9',  title: 'В.9',  subtitle: 'Эффективность СКО' },
  { id: 'v10', title: 'В.10', subtitle: 'Объёмы продав. и вытесняющей' },
  { id: 'v11', title: 'В.11', subtitle: 'Рецептура' },
  { id: 'v17', title: 'В.17', subtitle: 'Количество реагентов' },
];

export function ScreenResults({ results, onOpenTask }: Props) {
  if (!results) {
    return (
      <div style={{
        height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center',
        color: T.text2, fontFamily: T.mono, fontSize: 12,
      }}>
        Сначала заполните «Исходные данные» и нажмите «посчитать».
      </div>
    );
  }

  const tasks = (results.tasks || {}) as Record<string, TaskRes>;

  return (
    <div style={{ padding: '24px 28px', display: 'flex', flexDirection: 'column', gap: 18 }}>
      <div>
        <Tag>STIMCORE · RESULTS</Tag>
        <div style={{ fontSize: 22, fontWeight: 700, color: T.text0, letterSpacing: '-0.02em', marginTop: 4 }}>
          Результаты расчётов
        </div>
        <div style={{ fontFamily: T.mono, fontSize: 11, color: T.text2, marginTop: 4 }}>
          12 задач · клик по плитке — подробная страница
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
        {TASKS.map(t => {
          const data = tasks[t.id] as TaskRes | undefined;
          return (
            <TaskTile key={t.id} task={t} data={data} onClick={() => onOpenTask(t.id)} />
          );
        })}
      </div>
    </div>
  );
}


// ────────── tile ──────────
function TaskTile({
  task, data, onClick,
}: { task: { id: string; title: string; subtitle: string }; data: TaskRes | undefined; onClick: () => void }) {
  const summary = makeSummary(task.id, data);
  const status  = makeStatus(task.id, data);

  const glow = status.color;
  return (
    <button
      onClick={onClick}
      disabled={!data || (data as TaskRes).status === 'stub'}
      style={{
        textAlign: 'left', cursor: 'pointer',
        background: T.bg2, border: `1px solid ${glow}33`, borderRadius: 8,
        padding: 0, color: 'inherit',
        boxShadow: `0 0 12px ${glow}10`,
        transition: 'all .15s',
        opacity: data ? 1 : 0.4,
      }}
      onMouseEnter={e => {
        e.currentTarget.style.borderColor = glow + '99';
        e.currentTarget.style.boxShadow = `0 0 22px ${glow}25`;
        e.currentTarget.style.transform = 'translateY(-1px)';
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = glow + '33';
        e.currentTarget.style.boxShadow = `0 0 12px ${glow}10`;
        e.currentTarget.style.transform = 'translateY(0)';
      }}
    >
      <div style={{
        padding: '10px 14px', borderBottom: `1px solid ${T.border}`,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Dot color={glow} size={6} />
          <span style={{
            fontFamily: T.mono, fontSize: 10, fontWeight: 700, color: glow,
            letterSpacing: '0.16em', textTransform: 'uppercase',
          }}>{task.title}</span>
        </div>
        <span style={{
          fontFamily: T.mono, fontSize: 9, color: T.text3,
          letterSpacing: '0.1em', textTransform: 'uppercase',
        }}>{status.label}</span>
      </div>
      <div style={{ padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 8, minHeight: 92 }}>
        <div style={{ fontSize: 12, color: T.text1, lineHeight: 1.4 }}>{task.subtitle}</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginTop: 4 }}>
          {summary.map((s, i) => (
            <div key={i} style={{
              display: 'flex', alignItems: 'baseline', justifyContent: 'space-between',
              fontFamily: T.mono, fontSize: 11,
            }}>
              <span style={{ color: T.text3 }}>{s.label}</span>
              <span style={{ color: s.color || T.accent, fontWeight: 600 }}>
                {s.value}{s.unit ? <span style={{ color: T.text3, marginLeft: 4 }}>{s.unit}</span> : null}
              </span>
            </div>
          ))}
        </div>
      </div>
      <div style={{
        padding: '8px 14px', borderTop: `1px solid ${T.border}`,
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        fontFamily: T.mono, fontSize: 10, color: T.text2,
      }}>
        <span>подробнее</span>
        <span style={{ color: glow, fontSize: 14 }}>→</span>
      </div>
    </button>
  );
}


// ────────── summaries ──────────
type Item = { label: string; value: ReactNode; unit?: string; color?: string };

function makeSummary(id: string, d: TaskRes | undefined): Item[] {
  if (!d) return [{ label: '—', value: 'нет данных', color: T.text3 }];
  if ((d as TaskRes).status === 'stub') return [{ label: '—', value: 'в разработке', color: T.text3 }];

  switch (id) {
    case 'v1': return [
      { label: 'ОП', value: fmt(d.OP, 3), color: (d.cond_OP as boolean) ? T.green : T.red },
      { label: 'k_msg', value: fmt(d.k_msg, 3), color: (d.cond_kmsg as boolean) ? T.green : T.red },
      { label: 'k_в.о', value: fmt(d.k_vo_calc, 3), color: T.accent },
    ];
    case 'v2': return [
      { label: 'Q_ож', value: fmt(d.Q_oj, 2), unit: 'м³/сут' },
      { label: 'ОД', value: fmt(d.OD, 3), color: (d.cond_OD as boolean) ? T.green : T.red },
      { label: 'ε_от', value: fmt(d.e_ot, 3), color: (d.cond_e as boolean) ? T.green : T.red },
    ];
    case 'v3': return [
      { label: 'p_гст', value: fmt(d.p_gst, 2), unit: 'МПа', color: T.purple },
      { label: 'grad p_к', value: fmt(d.grad_p_k_fact, 3), color: (d.cond_grp as boolean) ? T.green : T.red },
      { label: 'grad p_грп', value: fmt(d.grad_p_grp, 3), color: T.orange },
    ];
    case 'v5': return [
      { label: 'r_з.р', value: fmt(d.r_zr, 3), unit: 'м', color: T.accent },
      { label: 'r_пр.р', value: fmt(d.r_pr_p, 3), unit: 'м' },
      { label: 'k_ms', value: fmt(d.k_ms, 3), color: T.green },
    ];
    case 'v6': return [
      { label: 'DG_s', value: fmt(d.DG_s, 3), unit: '%', color: T.green },
      { label: 'G_s', value: fmt(d.G_s_point, 1), unit: 'кг' },
    ];
    case 'v7': return [
      { label: 'DV_s', value: fmt(d.DV_s, 3), unit: '%', color: T.purple },
      { label: 'm_s', value: fmt(d.m_s, 2), unit: '%' },
      { label: 'k_ms', value: fmt(d.k_ms, 3) },
    ];
    case 'v8': return [
      { label: 'k_0', value: fmt(d.k0, 6), unit: 'мкм²', color: T.orange },
      { label: 'k_s', value: fmt(d.ks, 6), unit: 'мкм²' },
      { label: 'k_g', value: fmt(d.kg, 6), unit: 'мкм²' },
    ];
    case 'v9': return [
      { label: 'A_s', value: fmt(d.A_s, 3), color: T.accent },
      { label: 'ΔQ_н', value: fmt(d.DQ_n, 1), unit: 'т', color: T.green },
      { label: 'Э_н', value: money(d.E_n), unit: 'руб',
        color: (d.E_n as number) > 0 ? T.green : T.red },
    ];
    case 'v10': return [
      { label: 'V_прд', value: fmt(d.V_prd, 3), unit: 'м³', color: T.orange },
      { label: 'V_втс (с/з)', value: fmt(d.V_vts_57, 3), unit: 'м³', color: T.green },
      { label: 'V_total', value: fmt(d.V_total_57, 3), unit: 'м³', color: T.accent },
    ];
    case 'v11': return [
      { label: 'тип', value: shorten(String(d.type), 28), color: T.text0 },
      { label: 'y (HF)', value: `${d.y_HF as number} %`, color: T.accent },
      { label: 'ингиб.', value: ((d.inhibitor as TaskRes)?.name as string) || '—', color: T.green },
    ];
    case 'v17': {
      const opts = Object.keys(d as Record<string, TaskRes>);
      return [
        { label: 'товарная HCl', value: opts.map(o => `${o}%`).join(', '), color: T.purple },
        { label: 'вариантов', value: opts.length },
      ];
    }
    default: return [];
  }
}

function makeStatus(id: string, d: TaskRes | undefined): { label: string; color: string } {
  if (!d) return { label: 'нет данных', color: T.text3 };
  if ((d as TaskRes).status === 'stub') return { label: 'заглушка', color: T.text3 };
  if (id === 'v1' || id === 'v2' || id === 'v3') {
    return (d.decision as boolean)
      ? { label: 'OK', color: T.green }
      : { label: 'FAIL', color: T.red };
  }
  return { label: 'ready', color: T.accent };
}

function fmt(v: unknown, n: number): string {
  if (typeof v !== 'number' || !Number.isFinite(v)) return '—';
  return v.toFixed(n);
}
function money(v: unknown): string {
  if (typeof v !== 'number' || !Number.isFinite(v)) return '—';
  const sign = v < 0 ? '−' : '';
  return sign + Math.abs(v).toLocaleString('ru-RU', { maximumFractionDigits: 0 });
}
function shorten(s: string, max: number): string {
  return s.length > max ? s.slice(0, max - 1) + '…' : s;
}
