import { useState } from 'react'
import {
  BarChart3,
  Bot,
  ChevronRight,
  CircleDollarSign,
  Clock3,
  Moon,
  Plus,
  Send,
  ShieldCheck,
  Sparkles,
  Sun,
  TrendingUp,
  WalletCards,
} from 'lucide-react'
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import './App.css'

type Role = 'user' | 'assistant'

type ChartPoint = Record<string, string | number>

type ChartConfig = {
  type?: 'area' | 'bar' | 'line'
  title?: string
  eyebrow?: string
  data: ChartPoint[]
  xKey?: string
  yKey?: string
  xLabel?: string
  yLabel?: string
}

type AnalysisSummary = {
  total_contributed?: number
  investment_growth?: number
  projected_balance?: number
  initial_investment?: number
  monthly_contribution?: number
  annual_return?: number
  period_years?: number
}

type Message = {
  id: number
  role: Role
  content: string
  chart?: ChartConfig
  analysis?: AnalysisSummary
}

type Conversation = {
  id: number
  title: string
  time: string
}

const API_URL =
  import.meta.env.VITE_API_URL ||
  'http://127.0.0.1:8000'

const initialConversations: Conversation[] = [
  {
    id: 1,
    title: 'Investment growth analysis',
    time: 'Just now',
  },
  {
    id: 2,
    title: 'Understanding diversification',
    time: 'Yesterday',
  },
  {
    id: 3,
    title: 'Emergency fund planning',
    time: '2 days ago',
  },
  {
    id: 4,
    title: 'Risk vs. return',
    time: '3 days ago',
  },
]

function isNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value)
}

function normalizeNumber(
  value: unknown,
): number | undefined {
  if (isNumber(value)) {
    return value
  }

  if (typeof value === 'string') {
    const parsed = Number(
      value.replace(/[$,%]/g, ''),
    )

    if (Number.isFinite(parsed)) {
      return parsed
    }
  }

  return undefined
}

function normalizeChart(
  rawChart: unknown,
): ChartConfig | undefined {
  if (!rawChart || typeof rawChart !== 'object') {
    return undefined
  }

  const chart =
    rawChart as Record<string, unknown>

  const rawData =
    chart.data ??
    chart.points ??
    chart.values ??
    chart.dataset

  if (
    !Array.isArray(rawData) ||
    rawData.length === 0
  ) {
    return undefined
  }

  const data = rawData.filter(
    (item): item is ChartPoint =>
      Boolean(item) &&
      typeof item === 'object' &&
      !Array.isArray(item),
  )

  if (data.length === 0) {
    return undefined
  }

  let type: 'area' | 'bar' | 'line' = 'area'

  if (
    chart.type === 'bar' ||
    chart.type === 'line' ||
    chart.type === 'area'
  ) {
    type = chart.type
  }

  return {
    type,

    title:
      typeof chart.title === 'string'
        ? chart.title
        : 'Financial Projection',

    eyebrow:
      typeof chart.eyebrow === 'string'
        ? chart.eyebrow
        : 'ANALYSIS',

    data,

    xKey:
      typeof chart.xKey === 'string'
        ? chart.xKey
        : typeof chart.x_axis === 'string'
          ? chart.x_axis
          : Object.keys(data[0])[0],

    yKey:
      typeof chart.yKey === 'string'
        ? chart.yKey
        : typeof chart.y_axis === 'string'
          ? chart.y_axis
          : Object.keys(data[0])[1],

    xLabel:
      typeof chart.xLabel === 'string'
        ? chart.xLabel
        : undefined,

    yLabel:
      typeof chart.yLabel === 'string'
        ? chart.yLabel
        : undefined,
  }
}

function normalizeAnalysis(
  rawAnalysis: unknown,
): AnalysisSummary | undefined {
  if (
    !rawAnalysis ||
    typeof rawAnalysis !== 'object'
  ) {
    return undefined
  }

  const analysis =
    rawAnalysis as Record<string, unknown>

  return {
    total_contributed: normalizeNumber(
      analysis.total_contributed ??
        analysis.totalContributed ??
        analysis.total_invested,
    ),

    investment_growth: normalizeNumber(
      analysis.investment_growth ??
        analysis.investmentGrowth ??
        analysis.growth,
    ),

    projected_balance: normalizeNumber(
      analysis.projected_balance ??
        analysis.projectedBalance ??
        analysis.final_balance ??
        analysis.finalBalance,
    ),

    initial_investment: normalizeNumber(
      analysis.initial_investment ??
        analysis.initialInvestment,
    ),

    monthly_contribution: normalizeNumber(
      analysis.monthly_contribution ??
        analysis.monthlyContribution,
    ),

    annual_return: normalizeNumber(
      analysis.annual_return ??
        analysis.annualReturn ??
        analysis.return_rate,
    ),

    period_years: normalizeNumber(
      analysis.period_years ??
        analysis.periodYears ??
        analysis.years,
    ),
  }
}

function extractAssistantText(
  response: Record<string, unknown>,
): string {
  const candidates = [
    response.response,
    response.answer,
    response.content,
    response.message,
    response.text,
  ]

  for (const candidate of candidates) {
    if (
      typeof candidate === 'string' &&
      candidate.trim()
    ) {
      return candidate
    }
  }

  return 'I received a response from the FinAI backend, but no answer text was returned.'
}

function extractChart(
  response: Record<string, unknown>,
): ChartConfig | undefined {
  const candidates = [
    response.chart,
    response.chart_data,
    response.chartData,
    response.visualization,
    response.visual,
  ]

  for (const candidate of candidates) {
    const chart = normalizeChart(candidate)

    if (chart) {
      return chart
    }
  }

  return undefined
}

function extractAnalysis(
  response: Record<string, unknown>,
): AnalysisSummary | undefined {
  const candidates = [
    response.analysis,
    response.summary,
    response.financial_analysis,
    response.financialAnalysis,
  ]

  for (const candidate of candidates) {
    const analysis = normalizeAnalysis(candidate)

    if (analysis) {
      return analysis
    }
  }

  return undefined
}

function formatCurrency(
  value: number | undefined,
) {
  if (value === undefined) {
    return '—'
  }

  return `$${value.toLocaleString(undefined, {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  })}`
}

function formatPercent(
  value: number | undefined,
) {
  if (value === undefined) {
    return '—'
  }

  return `${value}%`
}

function ChartCard({
  chart,
  analysis,
  darkMode,
}: {
  chart: ChartConfig
  analysis?: AnalysisSummary
  darkMode: boolean
}) {
  const xKey = chart.xKey || 'x'
  const yKey = chart.yKey || 'y'

  return (
    <div className="analysis-card">
      <div className="analysis-header">
        <div>
          <div className="analysis-eyebrow">
            {chart.eyebrow || 'ANALYSIS'}
          </div>

          <h3>
            {chart.title || 'Financial Analysis'}
          </h3>
        </div>

        <div className="analysis-icon">
          <TrendingUp size={17} />
        </div>
      </div>

      {analysis && (
        <div className="analysis-summary">
          {analysis.total_contributed !==
            undefined && (
            <div>
              <span>
                Total contributed
              </span>

              <strong>
                {formatCurrency(
                  analysis.total_contributed,
                )}
              </strong>
            </div>
          )}

          {analysis.investment_growth !==
            undefined && (
            <div>
              <span>
                Investment growth
              </span>

              <strong>
                {formatCurrency(
                  analysis.investment_growth,
                )}
              </strong>
            </div>
          )}

          {analysis.projected_balance !==
            undefined && (
            <div>
              <span>
                Projected balance
              </span>

              <strong>
                {formatCurrency(
                  analysis.projected_balance,
                )}
              </strong>
            </div>
          )}
        </div>
      )}

      <div className="chart-wrapper">
        <ResponsiveContainer
          width="100%"
          height="100%"
        >
          {chart.type === 'bar' ? (
            <BarChart data={chart.data}>
              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
                stroke={
                  darkMode
                    ? 'rgba(255,255,255,0.08)'
                    : 'rgba(23,32,51,0.08)'
                }
              />

              <XAxis
                dataKey={xKey}
                axisLine={false}
                tickLine={false}
                tick={{
                  fontSize: 9,
                  fill: darkMode
                    ? '#9da7b8'
                    : '#687084',
                }}
              />

              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{
                  fontSize: 9,
                  fill: darkMode
                    ? '#9da7b8'
                    : '#687084',
                }}
                tickFormatter={(value) =>
                  typeof value === 'number'
                    ? `$${Math.round(
                        value / 1000,
                      )}k`
                    : String(value)
                }
              />

              <Tooltip
                formatter={(value) =>
                  typeof value === 'number'
                    ? `$${value.toLocaleString()}`
                    : String(value)
                }
              />

              <Bar
                dataKey={yKey}
                fill="#c99a3a"
                radius={[5, 5, 0, 0]}
              />
            </BarChart>
          ) : chart.type === 'line' ? (
            <LineChart data={chart.data}>
              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
                stroke={
                  darkMode
                    ? 'rgba(255,255,255,0.08)'
                    : 'rgba(23,32,51,0.08)'
                }
              />

              <XAxis
                dataKey={xKey}
                axisLine={false}
                tickLine={false}
                tick={{
                  fontSize: 9,
                  fill: darkMode
                    ? '#9da7b8'
                    : '#687084',
                }}
              />

              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{
                  fontSize: 9,
                  fill: darkMode
                    ? '#9da7b8'
                    : '#687084',
                }}
                tickFormatter={(value) =>
                  typeof value === 'number'
                    ? `$${Math.round(
                        value / 1000,
                      )}k`
                    : String(value)
                }
              />

              <Tooltip
                formatter={(value) =>
                  typeof value === 'number'
                    ? `$${value.toLocaleString()}`
                    : String(value)
                }
              />

              <Line
                type="monotone"
                dataKey={yKey}
                stroke="#c99a3a"
                strokeWidth={2.5}
                dot={false}
              />
            </LineChart>
          ) : (
            <AreaChart data={chart.data}>
              <defs>
                <linearGradient
                  id="investmentGradient"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop
                    offset="0%"
                    stopColor="#c99a3a"
                    stopOpacity={0.32}
                  />

                  <stop
                    offset="100%"
                    stopColor="#c99a3a"
                    stopOpacity={0}
                  />
                </linearGradient>
              </defs>

              <CartesianGrid
                strokeDasharray="3 3"
                vertical={false}
                stroke={
                  darkMode
                    ? 'rgba(255,255,255,0.08)'
                    : 'rgba(23,32,51,0.08)'
                }
              />

              <XAxis
                dataKey={xKey}
                axisLine={false}
                tickLine={false}
                tick={{
                  fontSize: 9,
                  fill: darkMode
                    ? '#9da7b8'
                    : '#687084',
                }}
              />

              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{
                  fontSize: 9,
                  fill: darkMode
                    ? '#9da7b8'
                    : '#687084',
                }}
                tickFormatter={(value) =>
                  typeof value === 'number'
                    ? `$${Math.round(
                        value / 1000,
                      )}k`
                    : String(value)
                }
              />

              <Tooltip
                formatter={(value) =>
                  typeof value === 'number'
                    ? `$${value.toLocaleString()}`
                    : String(value)
                }
                contentStyle={{
                  borderRadius: 10,
                  border: darkMode
                    ? '1px solid rgba(255,255,255,0.1)'
                    : '1px solid rgba(23,32,51,0.08)',
                  background: darkMode
                    ? '#182231'
                    : '#fffdf8',
                  fontSize: 11,
                }}
              />

              <Area
                type="monotone"
                dataKey={yKey}
                stroke="#c99a3a"
                strokeWidth={2.5}
                fill="url(#investmentGradient)"
              />
            </AreaChart>
          )}
        </ResponsiveContainer>
      </div>

      {analysis && (
        <div className="analysis-footer">
          {analysis.initial_investment !==
            undefined && (
            <span>
              Initial investment:{' '}
              {formatCurrency(
                analysis.initial_investment,
              )}
            </span>
          )}

          {analysis.monthly_contribution !==
            undefined && (
            <span>
              Monthly contribution:{' '}
              {formatCurrency(
                analysis.monthly_contribution,
              )}
            </span>
          )}

          {analysis.annual_return !==
            undefined && (
            <span>
              Assumed return:{' '}
              {formatPercent(
                analysis.annual_return,
              )}
            </span>
          )}

          {analysis.period_years !==
            undefined && (
            <span>
              Period:{' '}
              {analysis.period_years} years
            </span>
          )}
        </div>
      )}
    </div>
  )
}

function App() {
  const [darkMode, setDarkMode] =
    useState(false)

  const [input, setInput] =
    useState('')

  const [isLoading, setIsLoading] =
    useState(false)

  const [backendError, setBackendError] =
    useState('')

  const [conversations, setConversations] =
    useState(initialConversations)

  const [activeConversation, setActiveConversation] =
    useState(1)

  /*
   * The application starts with an empty
   * conversation.
   *
   * Therefore the landing header is shown
   * initially and disappears after the first
   * user message is sent.
   */
  const [messages, setMessages] =
    useState<Message[]>([])

  const handleSend = async () => {
    const trimmedInput = input.trim()

    if (!trimmedInput || isLoading) {
      return
    }

    const newUserMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: trimmedInput,
    }

    setMessages((currentMessages) => [
      ...currentMessages,
      newUserMessage,
    ])

    setInput('')
    setBackendError('')
    setIsLoading(true)

    try {
      /*
       * =====================================================
       * FINAI BACKEND PIPELINE
       *
       * Frontend
       *    ↓
       * POST /chat
       *    ↓
       * FastAPI backend
       *    ↓
       * RAG + financial tools
       *    ↓
       * grounded answer + optional chart data
       *    ↓
       * Frontend renders answer/chart
       * =====================================================
       */

      const response = await fetch(
        `${API_URL}/chat`,
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json',
          },

          body: JSON.stringify({
            question: trimmedInput,
            conversation_id:
              String(activeConversation),
          }),
        },
      )

      if (!response.ok) {
        const errorText =
          await response.text()

        throw new Error(
          `Backend returned ${response.status}: ${
            errorText ||
            response.statusText
          }`,
        )
      }

      const data: Record<
        string,
        unknown
      > = await response.json()

      const assistantText =
        extractAssistantText(data)

      const chart =
        extractChart(data)

      const analysis =
        extractAnalysis(data)

      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: assistantText,
        chart,
        analysis,
      }

      setMessages((currentMessages) => [
        ...currentMessages,
        assistantMessage,
      ])

      /*
       * If the backend gives us a conversation ID,
       * keep it available for future requests.
       */

      const returnedConversationId =
        data.conversation_id ??
        data.conversationId

      if (
        typeof returnedConversationId ===
        'number'
      ) {
        setActiveConversation(
          returnedConversationId,
        )
      }
    } catch (error) {
      console.error(
        'FinAI /chat request failed:',
        error,
      )

      const errorMessage =
        error instanceof Error
          ? error.message
          : 'Unknown backend error.'

      setBackendError(errorMessage)

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: Date.now() + 1,
          role: 'assistant',
          content:
            'I could not reach the FinAI backend. Please make sure the FastAPI server is running and that POST /chat is available.',
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleNewConversation = () => {
    const newId = Date.now()

    const newConversation: Conversation = {
      id: newId,
      title: 'New financial analysis',
      time: 'Just now',
    }

    setConversations(
      (currentConversations) => [
        newConversation,
        ...currentConversations,
      ],
    )

    setActiveConversation(newId)

    /*
     * Reset to the landing screen.
     */
    setMessages([])

    setInput('')
    setBackendError('')
  }

  const handleSuggestion = (
    question: string,
  ) => {
    setInput(question)
  }

  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLTextAreaElement>,
  ) => {
    if (
      event.key === 'Enter' &&
      !event.shiftKey
    ) {
      event.preventDefault()
      handleSend()
    }
  }

  /*
   * IMPORTANT:
   *
   * messages.length === 0
   *    → Landing header is visible
   *
   * messages.length > 0
   *    → Landing header disappears
   *
   * This is what makes the interface transition
   * from the clean welcome screen into the
   * actual chat interface.
   */
  const showLandingHeader =
    messages.length === 0

  return (
    <div
      className={`app ${
        darkMode ? 'dark' : ''
      }`}
    >
      {/* =====================================================
          SIDEBAR
          ===================================================== */}

      <aside className="sidebar">
        <div className="sidebar-top">
          <div className="brand">
            <div className="brand-mark">
              <BarChart3
                size={21}
                strokeWidth={2.2}
              />
            </div>

            <div>
              <div className="brand-name">
                FinAI
              </div>

              <div className="brand-subtitle">
                Intelligent Finance
              </div>
            </div>
          </div>

          <button
            className="new-conversation"
            type="button"
            onClick={
              handleNewConversation
            }
          >
            <Plus size={17} />

            <span>
              New conversation
            </span>
          </button>

          <div className="conversation-label">
            CONVERSATIONS
          </div>

          <div className="conversation-list">
            {conversations.map(
              (conversation) => (
                <button
                  key={conversation.id}
                  type="button"
                  className={`conversation-item ${
                    activeConversation ===
                    conversation.id
                      ? 'active'
                      : ''
                  }`}
                  onClick={() =>
                    setActiveConversation(
                      conversation.id,
                    )
                  }
                >
                  <div className="conversation-icon">
                    <Clock3 size={15} />
                  </div>

                  <div className="conversation-info">
                    <span className="conversation-title">
                      {
                        conversation.title
                      }
                    </span>

                    <span className="conversation-time">
                      {
                        conversation.time
                      }
                    </span>
                  </div>
                </button>
              ),
            )}
          </div>
        </div>

        <div className="sidebar-bottom">
          <button
            className="sidebar-action"
            type="button"
          >
            <ShieldCheck size={16} />

            <span>
              Privacy & security
            </span>
          </button>

          <div className="profile">
            <div className="profile-avatar">
              AS
            </div>

            <div className="profile-info">
              <span className="profile-name">
                Ahmed Samy
              </span>

              <span className="profile-plan">
                FinAI Personal
              </span>
            </div>
          </div>
        </div>
      </aside>

      {/* =====================================================
          MAIN APPLICATION AREA
          ===================================================== */}

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">
            <CircleDollarSign size={15} />

            <span>
              Investment Analyzer
            </span>

            <ChevronRight size={13} />

            <span>
              Analysis
            </span>
          </div>

          <div className="topbar-actions">
            <div className="status">
              <span
                className={`status-dot ${
                  isLoading
                    ? 'loading'
                    : ''
                }`}
              />

              <span>
                {isLoading
                  ? 'FinAI is analyzing...'
                  : 'AI system online'}
              </span>
            </div>

            <button
              className="theme-button"
              type="button"
              onClick={() =>
                setDarkMode(
                  (current) =>
                    !current,
                )
              }
              aria-label="Toggle theme"
            >
              {darkMode ? (
                <Sun size={16} />
              ) : (
                <Moon size={16} />
              )}
            </button>
          </div>
        </header>

        {/* =====================================================
            WORKSPACE
            ===================================================== */}

        <div
          className={`workspace ${
            showLandingHeader
              ? 'landing-mode'
              : 'chat-mode'
          }`}
        >
          {/* =================================================
              LANDING HEADER

              This entire section disappears automatically
              once the user sends the first question.
              ================================================= */}

          {showLandingHeader && (
            <div className="workspace-header">
              <div>
                <div className="eyebrow">
                  <Sparkles size={12} />

                  AI-POWERED FINANCIAL
                  ANALYSIS
                </div>

                <h1>
                  Understand your money.
                  <br />
                  Make better decisions.
                </h1>

                <p>
                  Ask FinAI about
                  investments, savings,
                  loans, financial
                  concepts, or long-term
                  wealth projections.
                </p>
              </div>

              <div className="analyzer-badge">
                <TrendingUp size={14} />

                Investment Analyzer
              </div>
            </div>
          )}

          {/* =================================================
              CHAT AREA
              ================================================= */}

          <section className="chat-container">
            <div className="messages">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`message-row ${
                    message.role ===
                    'user'
                      ? 'user-message'
                      : 'assistant-message'
                  }`}
                >
                  {message.role ===
                    'assistant' && (
                    <div className="assistant-avatar">
                      <Bot size={17} />
                    </div>
                  )}

                  <div className="message-content">
                    <span className="message-label">
                      {message.role ===
                      'user'
                        ? 'You'
                        : 'FinAI'}
                    </span>

                    <div className="message-bubble">
                      {message.content}
                    </div>

                    {message.chart && (
                      <ChartCard
                        chart={
                          message.chart
                        }
                        analysis={
                          message.analysis
                        }
                        darkMode={
                          darkMode
                        }
                      />
                    )}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="message-row assistant-message">
                  <div className="assistant-avatar">
                    <Bot size={17} />
                  </div>

                  <div className="message-content">
                    <span className="message-label">
                      FinAI
                    </span>

                    <div className="message-bubble">
                      Analyzing your
                      question...
                    </div>
                  </div>
                </div>
              )}
            </div>

            {backendError && (
              <div
                style={{
                  marginTop: 10,
                  padding: '10px 12px',
                  borderRadius: 8,
                  fontSize: 12,
                  background:
                    'rgba(220, 38, 38, 0.08)',
                  color: darkMode
                    ? '#ffb4b4'
                    : '#b42318',
                }}
              >
                Backend connection
                error:{' '}
                {backendError}
              </div>
            )}

            {/* =================================================
                SUGGESTIONS
                ================================================= */}

            {messages.length === 0 && (
              <div className="suggestions">
                <button
                  type="button"
                  onClick={() =>
                    handleSuggestion(
                      'What is diversification and why is it important?',
                    )
                  }
                >
                  <WalletCards size={13} />

                  Explain diversification
                </button>

                <button
                  type="button"
                  onClick={() =>
                    handleSuggestion(
                      'What will $500 monthly become after 20 years at 7%?',
                    )
                  }
                >
                  <TrendingUp size={13} />

                  Calculate investment
                  growth
                </button>

                <button
                  type="button"
                  onClick={() =>
                    handleSuggestion(
                      'What should I know before taking a loan?',
                    )
                  }
                >
                  <CircleDollarSign
                    size={13}
                  />

                  Analyze a loan
                </button>
              </div>
            )}

            {/* =================================================
                MESSAGE COMPOSER
                ================================================= */}

            <div className="composer">
              <textarea
                value={input}
                onChange={(event) =>
                  setInput(
                    event.target.value,
                  )
                }
                onKeyDown={handleKeyDown}
                placeholder="Ask FinAI about your finances..."
                rows={1}
                disabled={isLoading}
              />

              <button
                className="send-button"
                type="button"
                onClick={handleSend}
                disabled={
                  !input.trim() ||
                  isLoading
                }
                aria-label="Send message"
              >
                <Send size={17} />
              </button>
            </div>

            <div className="composer-note">
              FinAI provides educational
              financial analysis, not
              personalized investment
              advice.
            </div>
          </section>
        </div>
      </main>
    </div>
  )
}

export default App