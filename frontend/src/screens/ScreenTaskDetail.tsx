import type { ReactNode, CSSProperties } from 'react';
import { T } from '../theme';
import { Card, CardHeader, Stat, Tag } from '../components/atoms';

interface Props {
  taskId: string;
  results: Record<string, unknown> | null;
  onBack: () => void;
  onOpenTask: (id: string) => void;
}

const TASK_TITLES: Record<string, string> = {
  v1:  'Выбор скважины (полная информация)',
  v2:  'Выбор скважины (ограниченная информация)',
  v3:  'Расход и давление при нагнетании',
  v4:  'Длительность реакции СКР',
  v5:  'Зона растворения СКР',
  v6:  'Растворённая порода (по составу)',
  v7:  'Изменение пористости',
  v8:  'Проницаемость',
  v9:  'Эффективность СКО',
  v10: 'Объёмы продав. и вытесняющей жидкостей',
  v11: 'Рецептура',
  v17: 'Количество товарных реагентов',
};
const ORDER = ['v1','v2','v3','v4','v5','v6','v7','v8','v9','v10','v11','v17'];

export function ScreenTaskDetail({ taskId, results, onBack, onOpenTask }: Props) {
  const tasks = ((results?.tasks) || {}) as Record<string, Record<string, unknown>>;
  const data = tasks[taskId];

  const idx = ORDER.indexOf(taskId);
  const prev = idx > 0 ? ORDER[idx - 1] : null;
  const next = idx >= 0 && idx < ORDER.length - 1 ? ORDER[idx + 1] : null;

  return (
    <div style={{ padding: '24px 28px', display: 'flex', flexDirection: 'column', gap: 18 }}>
      {/* breadcrumb */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <button onClick={onBack} style={navBtn}>← к обзору</button>
          {prev && <button onClick={() => onOpenTask(prev)} style={navBtn}>← {prev.toUpperCase()}</button>}
          {next && <button onClick={() => onOpenTask(next)} style={navBtn}>{next.toUpperCase()} →</button>}
        </div>
        <Tag>STIMCORE · DETAIL</Tag>
      </div>

      {/* heading */}
      <div>
        <div style={{
          fontFamily: T.mono, fontSize: 11, fontWeight: 700, color: T.accent,
          letterSpacing: '0.16em', textTransform: 'uppercase', marginBottom: 6,
        }}>{taskId.toUpperCase()}</div>
        <div style={{ fontSize: 22, fontWeight: 700, color: T.text0, letterSpacing: '-0.02em' }}>
          {TASK_TITLES[taskId] || 'Задача'}
        </div>
      </div>

      {!data
        ? <Empty>Данные не найдены — пересчитайте.</Empty>
        : <DetailRouter taskId={taskId} d={data} />
      }
    </div>
  );
}


// ────────── routing ──────────
function DetailRouter({ taskId, d }: { taskId: string; d: Record<string, unknown> }) {
  switch (taskId) {
    case 'v1':  return <V1  d={d} />;
    case 'v2':  return <V2  d={d} />;
    case 'v3':  return <V3  d={d} />;
    case 'v4':  return <Empty>Задача В.4 не реализована — заглушка.</Empty>;
    case 'v5':  return <V5  d={d} />;
    case 'v6':  return <V6  d={d} />;
    case 'v7':  return <V7  d={d} />;
    case 'v8':  return <V8  d={d} />;
    case 'v9':  return <V9  d={d} />;
    case 'v10': return <V10 d={d} />;
    case 'v11': return <V11 d={d} />;
    case 'v17': return <V17 d={d} />;
    default:    return <Empty>Неизвестная задача.</Empty>;
  }
}


// ════════════════ V.1 ════════════════
function V1({ d }: { d: Record<string, unknown> }) {
  const ok = d.decision as boolean;
  return (
    <>
      <Verdict ok={ok} okText={`КО целесообразна · ${d.treatment_type as string}`} failText="КО не рекомендуется" />
      <MetricsGrid items={[
        { label: 'K_ф',    value: fmt(d.K_f, 2),    unit: 'т/(сут·МПа)', color: T.accent },
        { label: 'K_пот',  value: fmt(d.K_pot, 2),  unit: 'т/(сут·МПа)', color: T.accent },
        { label: 'ОП',     value: fmt(d.OP, 4),     color: ok ? T.green : T.red },
        { label: 'h_пгл',  value: fmt(d.h_pta, 1),  unit: 'м' },
        { label: 'h_пр',   value: fmt(d.h_pr, 1),   unit: 'м' },
        { label: 'k_в.о',  value: fmt(d.k_vo_calc, 3), color: T.accent },
        { label: 'k_ms',   value: fmt(d.k_ms, 3) },
        { label: 'k_mg',   value: fmt(d.k_mg, 3) },
        { label: 'k_msg',  value: fmt(d.k_msg, 3),  color: (d.cond_kmsg as boolean) ? T.green : T.red },
      ]} />
      <CriteriaList items={[
        { label: 'В.1   ОП < 1',                  ok: d.cond_OP as boolean },
        { label: 'В.2   m₀ > m_гр (все пласты)',  ok: d.all_layers_ok as boolean },
        { label: 'В.3   h_пгл ≥ h_пр',            ok: d.cond_h as boolean },
        { label: 'В.4   k_ms ≥ 1.1',              ok: d.cond_kms as boolean },
        { label: 'В.5   k_mg ≥ 1.1',              ok: d.cond_kmg as boolean },
        { label: 'В.6   k_msg ≥ 1.21',            ok: d.cond_kmsg as boolean },
        { label: 'В.7   C_к ≥ C_к.пр',            ok: d.cond_Ck as boolean },
      ]} />
      <DataTable
        title="Пласты (m₀ > m_гр)"
        rows={d.layer_results as Record<string, unknown>[] | undefined}
        accent={T.accent}
      />
      <Note>Технология по разрезу: <strong style={{ color: T.text0 }}>{String(d.coverage_decision)}</strong></Note>
    </>
  );
}


// ════════════════ V.2 ════════════════
function V2({ d }: { d: Record<string, unknown> }) {
  const ok = d.decision as boolean;
  return (
    <>
      <Verdict ok={ok} okText="Все критерии выполнены" failText="Не все критерии выполнены" />
      <MetricsGrid items={[
        { label: 'Q_ф',     value: fmt(d.Q_f, 1),    unit: 'м³/сут' },
        { label: 'Q_ож',    value: fmt(d.Q_oj, 2),   unit: 'м³/сут', color: T.accent },
        { label: 'ОД',      value: fmt(d.OD, 4),     color: (d.cond_OD as boolean) ? T.green : T.red },
        { label: 'q (нагн.)', value: fmt(d.q_inj, 1),  unit: 'м³/сут' },
        { label: 'h_эф',    value: fmt(d.h_ef, 1),   unit: 'м' },
        { label: 'C_гл',    value: fmt(d.C_gl, 1),   unit: '%' },
        { label: 'ε_обр',   value: fmt(d.eps_obr, 4), unit: 'мкм²·м' },
        { label: 'ε_скв',   value: fmt(d.eps_skv, 4), unit: 'мкм²·м' },
        { label: 'ε_от',    value: fmt(d.e_ot, 3),   color: (d.cond_e as boolean) ? T.green : T.red },
        { label: 'p_гст',   value: fmt(d.p_gst, 3),  unit: 'МПа',  color: T.purple },
        { label: 'k_энр',   value: fmt(d.k_enr, 3),  color: (d.cond_enr as boolean) ? T.green : T.red },
      ]} />
      <CriteriaList items={[
        { label: 'В.8    ОД < 1',         ok: d.cond_OD as boolean },
        { label: 'В.10   q ≥ 24 м³/сут', ok: d.cond_q as boolean },
        { label: 'В.11   h_эф ≥ 5 м',    ok: d.cond_h as boolean },
        { label: 'В.12   C_гл ≤ 10 %',    ok: d.cond_Cgl as boolean },
        { label: 'В.13   ε_от > 0.5',    ok: d.cond_e as boolean },
        { label: 'В.14   k_энр > 0.7',   ok: d.cond_enr as boolean },
      ]} />
      <DataTable
        title="Расчёт по пластам"
        rows={d.layer_rows as Record<string, unknown>[] | undefined}
        accent={T.accent}
      />
    </>
  );
}


// ════════════════ V.3 ════════════════
function V3({ d }: { d: Record<string, unknown> }) {
  const ok = d.decision as boolean;
  return (
    <>
      <Verdict ok={ok}
        okText={`Параметры закачки обоснованы · q_к = ${fmt(d.q_k, 0)} м³/сут, p_к = ${fmt(d.p_k, 2)} МПа`}
        failText="Параметры не удовлетворяют условиям" />
      <MetricsGrid items={[
        { label: 'H',                value: fmt(d.H, 0),            unit: 'м' },
        { label: 'ρ',                value: fmt(d.rho, 0),          unit: 'кг/м³' },
        { label: 'p_гст',            value: fmt(d.p_gst, 3),        unit: 'МПа', color: T.purple },
        { label: 'grad p_грп',       value: fmt(d.grad_p_grp, 3),    unit: 'МПа/100м', color: T.orange },
        { label: 'p_грп забой',       value: fmt(d.p_grp_zab, 2),    unit: 'МПа' },
        { label: 'grad p_к норм',     value: fmt(d.grad_p_k_norm, 2), unit: 'МПа/100м' },
        { label: 'p_к норм',          value: fmt(d.p_k_norm, 2),      unit: 'МПа',     color: T.accent },
        { label: 'q_к',              value: fmt(d.q_k, 1),           unit: 'м³/сут' },
        { label: 'p_к',              value: fmt(d.p_k, 2),           unit: 'МПа' },
        { label: 'grad p_к факт.',    value: fmt(d.grad_p_k_fact, 3), unit: 'МПа/100м', color: (d.cond_grp as boolean) ? T.green : T.red },
      ]} />
      <CriteriaList items={[
        { label: 'В.10   q_к ≥ 24 м³/сут',          ok: d.cond_q_min as boolean },
        { label: 'В.15   p_к ≤ p_опр',              ok: d.cond_p_opr as boolean },
        { label: 'В.16   grad p_к < grad p_грп',     ok: d.cond_grp as boolean },
      ]} />
    </>
  );
}


// ════════════════ V.5 ════════════════
function V5({ d }: { d: Record<string, unknown> }) {
  const df = d.df as Record<string, unknown>[] | undefined;
  return (
    <>
      <MetricsGrid items={[
        { label: 'k_ms',     value: fmt(d.k_ms, 4),    color: T.green },
        { label: 'C_ms',     value: fmt(d.C_ms, 2),    unit: 'кг/м³' },
        { label: 'DC_s',     value: fmt(d.DC_s, 2),    unit: 'кг/м³' },
        { label: 'V_зад',    value: fmt(d.V_zad, 3),   unit: 'м³' },
        { label: 't_u',      value: fmt(d.t_u, 1),     unit: 'мин',  color: T.accent },
        { label: 'r_пр.р',   value: fmt(d.r_pr_p, 3),  unit: 'м' },
        { label: 'r_з.р',    value: fmt(d.r_zr, 3),    unit: 'м',    color: T.accent },
        { label: 'G_ms',     value: fmt(d.G_ms, 3),    unit: 'кг' },
        { label: 'G_s(зад)', value: fmt(d.G_s_zad, 1), unit: 'кг' },
        { label: 'm₀',       value: fmt(d.m_0, 2),     unit: '%' },
        { label: 'm_c',      value: fmt(d.m_c, 2),     unit: '%',    color: T.green },
      ]} />
      <DataTable
        title={`Профиль V_ks(r), G_s(r) — ${df?.length || 0} точек`}
        rows={df}
        accent={T.accent}
      />
    </>
  );
}


// ════════════════ V.6 ════════════════
function V6({ d }: { d: Record<string, unknown> }) {
  return (
    <>
      <MetricsGrid items={[
        { label: 'a',   value: fmt(d.a, 2) },
        { label: 'b',   value: fmt(d.b, 2) },
        { label: 'DG_s',          value: fmt(d.DG_s, 4),     unit: '%',  color: T.green },
        { label: 'G_s (по составу)',value: fmt(d.G_s_point, 1), unit: 'кг', color: T.green },
        { label: 'G_s (В.5 по k_ms)',value: fmt(d.G_s_v5, 1),    unit: 'кг' },
      ]} />
      <DataTable
        title="Сравнение G_s(r): В.6 (по составу) vs В.5 (по k_ms)"
        rows={d.df as Record<string, unknown>[] | undefined}
        accent={T.green}
      />
    </>
  );
}


// ════════════════ V.7 ════════════════
function V7({ d }: { d: Record<string, unknown> }) {
  return (
    <>
      <MetricsGrid items={[
        { label: 'DG_s',     value: fmt(d.DG_s, 4),  unit: '%', color: T.purple },
        { label: 'DV_s',     value: fmt(d.DV_s, 4),  unit: '%', color: T.purple },
        { label: 'm₀',       value: fmt(d.m_0, 2),   unit: '%' },
        { label: 'm_s',      value: fmt(d.m_s, 2),   unit: '%', color: T.green },
        { label: 'k_ms (косв.)', value: fmt(d.k_ms, 4),  color: T.purple },
        { label: 'k_ms (лаб.)',  value: fmt(d.k_ms_v5, 4) },
        { label: 'G_s', value: fmt(d.G_s_point, 1), unit: 'кг' },
      ]} />
      <DataTable
        title="Профиль G_s(r) (косв. метод)"
        rows={d.df as Record<string, unknown>[] | undefined}
        accent={T.purple}
      />
    </>
  );
}


// ════════════════ V.8 ════════════════
function V8({ d }: { d: Record<string, unknown> }) {
  return (
    <>
      <MetricsGrid items={[
        { label: 'КЛ',                value: String(d.KL_key) },
        { label: 'k_0 (рег.)',        value: fmt(d.k0_reg, 6),   unit: 'мкм²' },
        { label: 'k_0 (исп.)',        value: fmt(d.k0, 6),       unit: 'мкм²', color: T.orange },
        { label: 'k_s* (раз)',        value: fmt(d.ks_star, 3),  color: T.green },
        { label: 'k_s',               value: fmt(d.ks, 6),       unit: 'мкм²', color: T.green },
        { label: 'k_g* (раз)',        value: fmt(d.kg_star, 3),  color: T.purple },
        { label: 'k_g',               value: fmt(d.kg, 6),       unit: 'мкм²', color: T.purple },
        { label: 'формула',           value: d.n_exp === 3 ? 'В.46 (k₀<0.001)' : 'В.47 (k₀≥0.001)', color: T.accent },
        { label: 'прирост СКО',       value: '×' + fmt(d.growth_sko, 2) },
        { label: 'прирост СКО+ГКО',   value: '×' + fmt(d.growth_sko_gko, 2) },
        { label: 'эффект ГКО',        value: '×' + fmt(d.growth_gko, 2) },
      ]} />
    </>
  );
}


// ════════════════ V.9 ════════════════
function V9({ d }: { d: Record<string, unknown> }) {
  const inputs = (d.inputs || {}) as Record<string, unknown>;
  return (
    <>
      <MetricsGrid items={[
        { label: 'A_s',            value: fmt(d.A_s, 4),      color: T.accent },
        { label: 'Q_ф',            value: fmt(d.Q_f, 2),      unit: 'м³/сут' },
        { label: 'Q_s',            value: fmt(d.Q_s, 2),      unit: 'м³/сут', color: T.green },
        { label: 'ΔQ',             value: fmt(d.dQ, 2),       unit: 'м³/сут' },
        { label: 'ΔQ_н',           value: fmt(d.DQ_n, 1),     unit: 'т',      color: T.green },
        { label: 'ε_от (расч.)',   value: fmt(d.eps_ot_calc, 3) },
        { label: 'Э_н',            value: money(d.E_n),       unit: 'руб',
          color: (d.E_n as number) > 0 ? T.green : T.red },
        { label: 'окуп.',          value: fmt(d.payback_days, 1), unit: 'сут', color: T.orange },
      ]} />
      <Note>Метод: <strong style={{ color: T.text0 }}>{String(d.method)}</strong></Note>
      <Section title="Подстановка (В.50)">
        <code style={codeBlock}>
          A_s = ln({fmt(inputs.r_k, 0)}/{fmt(inputs.r_c, 3)}) / [({fmt(inputs.k0, 4)}/{fmt(inputs.k_s, 4)})·ln({fmt(inputs.r_zr, 3)}/{fmt(inputs.r_c, 3)}) + ln({fmt(inputs.r_k, 0)}/{fmt(inputs.r_pr, 3)})] = {fmt(d.A_s, 4)}
        </code>
      </Section>
    </>
  );
}


// ════════════════ V.10 ════════════════
function V10({ d }: { d: Record<string, unknown> }) {
  return (
    <MetricsGrid items={[
      { label: 'V_ks (зад.)', value: fmt(d.V_ks, 3),    unit: 'м³', color: T.accent },
      { label: 'V_зр',        value: fmt(d.V_zr, 4),    unit: 'м³' },
      { label: 'V_прд',       value: fmt(d.V_prd, 3),   unit: 'м³', color: T.orange },
      { label: 'V_втс (б/з)', value: fmt(d.V_vts_56, 3),unit: 'м³', color: T.accent },
      { label: 'V_втс (с/з)', value: fmt(d.V_vts_57, 3),unit: 'м³', color: T.green },
      { label: 'V_total (б/з)', value: fmt(d.V_total_56, 3), unit: 'м³' },
      { label: 'V_total (с/з)', value: fmt(d.V_total_57, 3), unit: 'м³', color: T.accent },
      { label: 't_total (б/з)', value: fmt(d.t_total_56, 1), unit: 'мин' },
      { label: 't_total (с/з)', value: fmt(d.t_total_57, 1), unit: 'мин', color: T.purple },
    ]} />
  );
}


// ════════════════ V.11 ════════════════
function V11({ d }: { d: Record<string, unknown> }) {
  const inhibitor  = d.inhibitor  as Record<string, unknown> | null;
  const stabilizer = d.stabilizer as Record<string, unknown> | null;
  const surf       = d.surfactant as Record<string, unknown> | null;
  const needs      = d.needs as Record<string, boolean>;

  return (
    <>
      <Card glow={T.accent}>
        <CardHeader title="Итоговая рецептура" accent={T.accent} />
        <div style={{ padding: 16, fontFamily: T.mono, fontSize: 13, color: T.text1, lineHeight: 1.9 }}>
          <Row k="Тип обработки"     v={String(d.treatment)} />
          <Row k="Тип КР"            v={String(d.type)}      vColor={T.accent} />
          <Row k="y (HF)"            v={`${d.y_HF as number} %`} vColor={T.accent} />
          <Row k="Ингибитор"
               v={inhibitor ? `${inhibitor.name as string} — ${inhibitor.conc as string}` : '—'}
               vColor={T.green} />
          <Row k="Стабилизатор"
               v={stabilizer ? `${stabilizer.name as string} — ${stabilizer.conc as string}` : '—'}
               vColor={T.purple} />
          <Row k="ПАВ"
               v={surf ? (surf.PAV_list as string[])?.[0] || '—' : '—'}
               vColor={T.orange} />
          <Row k="Продавочная"   v={String(d.buffer_fluid)} />
          <Row k="Вытесняющая"   v={String(d.buffer_fluid)} />
        </div>
      </Card>

      <MetricsGrid items={[
        { label: 'нужен ингибитор',   value: needs?.inhibitor  ? '✓' : '—', color: needs?.inhibitor ? T.green : T.text3 },
        { label: 'нужен стабилизатор', value: needs?.stabilizer ? '✓' : '—', color: needs?.stabilizer ? T.green : T.text3 },
        { label: 'нужен ПАВ',          value: needs?.surfactant ? '✓' : '—', color: needs?.surfactant ? T.green : T.text3 },
      ]} />

      {surf && (
        <Section title="Альтернативные ПАВ из табл. В.19">
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {((surf.PAV_list as string[]) || []).map((p, i) => (
              <span key={i} style={pavBadge}>{p}</span>
            ))}
          </div>
          <div style={{ marginTop: 10, fontFamily: T.mono, fontSize: 11, color: T.text2 }}>
            Условия: {((surf.rules as string[]) || []).join('; ')}
          </div>
        </Section>
      )}
    </>
  );
}


// ════════════════ V.17 ════════════════
function V17({ d }: { d: Record<string, unknown> }) {
  const opts = Object.entries(d as Record<string, Record<string, unknown>>);
  return (
    <>
      {opts.map(([tov, data]) => (
        <Card key={tov}>
          <CardHeader title={`Товарная HCl ${tov} %`} accent={T.purple} />
          <div style={{ padding: 14, display: 'flex', flexDirection: 'column', gap: 16 }}>
            <FluidTable title="СКР"                            rows={data.skr    as Record<string, unknown>[] | undefined} />
            <FluidTable title="Продавочная жидкость"          rows={data.prd    as Record<string, unknown>[] | undefined} />
            <FluidTable title="Вытесняющая (без запаса)"      rows={data.vts_56 as Record<string, unknown>[] | undefined} />
            <FluidTable title="Вытесняющая (с запасом)"       rows={data.vts_57 as Record<string, unknown>[] | undefined} />
          </div>
        </Card>
      ))}
    </>
  );
}

function FluidTable({ title, rows }: { title: string; rows: Record<string, unknown>[] | undefined }) {
  if (!rows?.length) return null;
  return (
    <div>
      <div style={{
        fontFamily: T.mono, fontSize: 10, fontWeight: 700,
        color: T.purple, letterSpacing: '0.16em', textTransform: 'uppercase', marginBottom: 6,
      }}>{title}</div>
      <DataTable title="" rows={rows} accent={T.purple} />
    </div>
  );
}


// ════════════════ shared blocks ════════════════
function Verdict({ ok, okText, failText }: { ok: boolean; okText: string; failText: string }) {
  const c = ok ? T.green : T.red;
  return (
    <div style={{
      background: c + '12', border: `1px solid ${c}55`,
      borderRadius: 8, padding: '14px 18px',
      fontFamily: T.mono, fontSize: 13, fontWeight: 700,
      color: c, letterSpacing: '0.06em',
    }}>
      {ok ? '✓ ' : '✗ '}{ok ? okText : failText}
    </div>
  );
}

function MetricsGrid({ items }: { items: { label: string; value: ReactNode; unit?: string; color?: string }[] }) {
  return (
    <Card>
      <CardHeader title="Метрики" accent={T.accent} />
      <div style={{ padding: 16, display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
        {items.map((it, i) => (
          <Stat key={i} label={it.label} value={it.value} unit={it.unit} color={it.color || T.accent} />
        ))}
      </div>
    </Card>
  );
}

function CriteriaList({ items }: { items: { label: string; ok: boolean }[] }) {
  return (
    <Card>
      <CardHeader title="Критерии" accent={T.green} />
      <div style={{ padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: 6 }}>
        {items.map((it, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, fontFamily: T.mono, fontSize: 12 }}>
            <span style={{
              width: 18, height: 18, borderRadius: 4,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: (it.ok ? T.green : T.red) + '22',
              color: it.ok ? T.green : T.red, fontWeight: 700,
            }}>{it.ok ? '✓' : '✗'}</span>
            <span style={{ color: it.ok ? T.text0 : T.text2 }}>{it.label}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}

function DataTable({
  title, rows, accent,
}: { title: string; rows: Record<string, unknown>[] | undefined; accent: string }) {
  if (!rows || !rows.length) return null;
  const cols = Object.keys(rows[0]);
  return (
    <Card>
      {title && <CardHeader title={title} accent={accent} />}
      <div style={{ padding: title ? 14 : 0, overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontFamily: T.mono, fontSize: 11 }}>
          <thead>
            <tr style={{ color: T.text2, background: T.bg1 }}>
              {cols.map(c => (
                <th key={c} style={th}>{c}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i} style={{ borderTop: `1px solid ${T.border}` }}>
                {cols.map(c => (
                  <td key={c} style={{
                    ...td,
                    color: typeof r[c] === 'number' ? accent : T.text1,
                    textAlign: typeof r[c] === 'number' ? 'right' : 'left',
                  }}>
                    {typeof r[c] === 'number' ? fmtAuto(r[c] as number) : String(r[c] ?? '')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Card>
      <CardHeader title={title} accent={T.accent} />
      <div style={{ padding: 16 }}>{children}</div>
    </Card>
  );
}

function Note({ children }: { children: ReactNode }) {
  return (
    <div style={{
      background: T.bg2, border: `1px solid ${T.border}`, borderLeft: `3px solid ${T.accent}`,
      borderRadius: 4, padding: '10px 14px',
      fontFamily: T.mono, fontSize: 12, color: T.text1,
    }}>{children}</div>
  );
}

function Empty({ children }: { children: ReactNode }) {
  return (
    <div style={{
      padding: 40, textAlign: 'center',
      color: T.text2, fontFamily: T.mono, fontSize: 12,
      border: `1px dashed ${T.border}`, borderRadius: 8,
    }}>{children}</div>
  );
}

function Row({ k, v, vColor }: { k: string; v: string; vColor?: string }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '180px 1fr', gap: 12 }}>
      <span style={{ color: T.text3 }}>{k}</span>
      <span style={{ color: vColor || T.text0 }}>{v}</span>
    </div>
  );
}


// ────────── helpers ──────────
function fmt(v: unknown, n: number): string {
  if (typeof v !== 'number' || !Number.isFinite(v)) return '—';
  return v.toFixed(n);
}
function money(v: unknown): string {
  if (typeof v !== 'number' || !Number.isFinite(v)) return '—';
  const sign = v < 0 ? '−' : '';
  return sign + Math.abs(v).toLocaleString('ru-RU', { maximumFractionDigits: 0 });
}
function fmtAuto(v: number): string {
  if (!Number.isFinite(v)) return '—';
  if (v === 0) return '0';
  const a = Math.abs(v);
  if (a >= 1000)  return v.toFixed(1);
  if (a >= 1)     return v.toFixed(3);
  if (a >= 0.001) return v.toFixed(5);
  return v.toExponential(3);
}


// ────────── styles ──────────
const navBtn: CSSProperties = {
  background: T.bg2, border: `1px solid ${T.border2}`, borderRadius: 5,
  color: T.text1, fontFamily: T.mono, fontSize: 10, fontWeight: 600,
  padding: '6px 12px', cursor: 'pointer',
  letterSpacing: '0.1em', textTransform: 'uppercase',
};
const th: CSSProperties = {
  padding: '8px 10px', textAlign: 'left',
  fontSize: 9, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase',
  borderBottom: `1px solid ${T.border2}`,
};
const td: CSSProperties = { padding: '6px 10px', whiteSpace: 'nowrap' };
const codeBlock: CSSProperties = {
  display: 'block', background: T.bg0, border: `1px solid ${T.border}`,
  borderLeft: `3px solid ${T.accent}`, borderRadius: 4,
  padding: '10px 14px', fontFamily: T.mono, fontSize: 11,
  color: T.text1, lineHeight: 1.6, whiteSpace: 'pre-wrap',
};
const pavBadge: CSSProperties = {
  background: T.bg1, border: `1px solid ${T.border}`, borderRadius: 4,
  padding: '4px 10px', fontFamily: T.mono, fontSize: 11, color: T.text1,
};
