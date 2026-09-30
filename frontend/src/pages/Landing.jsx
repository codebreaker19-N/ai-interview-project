import { Link } from "react-router-dom"

function Landing() {
  return (
    <main className="min-h-screen bg-[#f7f7f4] text-[#171717]">

      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5 lg:px-8">

        <Link to="/" className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#171717] text-sm font-semibold text-white">
            AI
          </div>

          <span className="text-lg font-semibold tracking-tight">
            Interview Coach
          </span>
        </Link>

        <div className="hidden items-center gap-8 text-sm text-gray-600 md:flex">
          <a href="#practice">Practice</a>
          <a href="#how-it-works">Mock Interview</a>
          <a href="#progress">Progress</a>
          <a href="#about">About</a>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/login"
            className="hidden px-4 py-2 text-sm font-medium text-gray-700 sm:block"
          >
            Login
          </Link>

          <Link
            to="/register"
            className="rounded-lg bg-[#171717] px-4 py-2.5 text-sm font-medium text-white transition hover:bg-gray-800"
          >
            Get Started
          </Link>
        </div>

      </nav>


      <section className="mx-auto grid max-w-7xl gap-16 px-6 pb-24 pt-20 lg:grid-cols-2 lg:items-center lg:px-8 lg:pt-28">

        <div>

          <p className="mb-5 text-sm font-medium text-indigo-600">
            AI-powered interview practice
          </p>

          <h1 className="max-w-2xl text-5xl font-semibold tracking-tight sm:text-6xl">
            Your interview answers deserve more than a score.
          </h1>

          <p className="mt-7 max-w-xl text-lg leading-8 text-gray-600">
            Practice technical interviews, get meaningful feedback,
            and understand exactly how to improve — one answer at a time.
          </p>

          <div className="mt-9 flex flex-wrap gap-3">

            <Link
              to="/register"
              className="rounded-xl bg-indigo-600 px-6 py-3.5 text-sm font-semibold text-white transition hover:bg-indigo-500"
            >
              Start Practicing
            </Link>

            <a
              href="#how-it-works"
              className="rounded-xl border border-gray-300 bg-white px-6 py-3.5 text-sm font-semibold text-gray-800 transition hover:bg-gray-50"
            >
              See How It Works
            </a>

          </div>

          <p className="mt-6 text-sm text-gray-500">
            Built for students, developers, and aspiring engineers.
          </p>

        </div>


        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-[0_20px_60px_rgba(0,0,0,0.08)]">

          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium uppercase tracking-wider text-gray-400">
                Interview evaluation
              </p>

              <h2 className="mt-1 font-semibold">
                Machine Learning
              </h2>
            </div>

            <span className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-600">
              Medium
            </span>
          </div>


          <div className="rounded-xl bg-gray-50 p-4">

            <p className="text-sm font-medium text-gray-500">
              Question
            </p>

            <p className="mt-2 text-sm leading-6 text-gray-800">
              Explain the difference between Bagging and Boosting.
            </p>

          </div>


          <div className="mt-4">

            <p className="text-sm font-medium text-gray-500">
              Your answer
            </p>

            <p className="mt-2 text-sm leading-6 text-gray-600">
              Bagging trains multiple models independently and combines
              their predictions, while boosting trains models sequentially
              to focus on previous errors.
            </p>

          </div>


          <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">

            {[
              ["Technical Accuracy", "92"],
              ["Concept Coverage", "88"],
              ["Clarity", "84"],
              ["Confidence", "79"],
            ].map(([label, value]) => (
              <div
                key={label}
                className="rounded-xl border border-gray-100 bg-white p-3"
              >
                <p className="text-xs leading-4 text-gray-500">
                  {label}
                </p>

                <p className="mt-2 text-xl font-semibold">
                  {value}
                </p>
              </div>
            ))}

          </div>


          <div className="mt-5 flex items-center justify-between rounded-xl bg-indigo-50 px-4 py-4">

            <div>
              <p className="text-xs font-medium text-indigo-600">
                Overall Score
              </p>

              <p className="mt-1 text-3xl font-semibold text-gray-900">
                87
              </p>
            </div>

            <div className="max-w-xs text-right text-xs leading-5 text-gray-600">
              You're on the right track. Consider explaining how boosting
              focuses on previous errors.
            </div>

          </div>

        </div>

      </section>


      <section
        id="how-it-works"
        className="border-y border-gray-200 bg-white"
      >

        <div className="mx-auto max-w-7xl px-6 py-20 lg:px-8">

          <div className="max-w-xl">
            <p className="text-sm font-medium text-indigo-600">
              How it works
            </p>

            <h2 className="mt-3 text-3xl font-semibold tracking-tight">
              Practice with a feedback loop that actually helps.
            </h2>
          </div>


          <div className="mt-12 grid gap-8 md:grid-cols-4">

            {[
              [
                "01",
                "Choose",
                "Choose a topic, difficulty, and interview type.",
              ],
              [
                "02",
                "Answer",
                "Answer the question like you're sitting in a real interview.",
              ],
              [
                "03",
                "Get Feedback",
                "Receive structured AI + ML-based evaluation.",
              ],
              [
                "04",
                "Improve",
                "Understand what you missed and practice again.",
              ],
            ].map(([number, title, description]) => (
              <div key={number} className="border-t border-gray-200 pt-5">

                <p className="text-sm font-medium text-gray-400">
                  {number}
                </p>

                <h3 className="mt-4 text-lg font-semibold">
                  {title}
                </h3>

                <p className="mt-2 text-sm leading-6 text-gray-600">
                  {description}
                </p>

              </div>
            ))}

          </div>

        </div>

      </section>


      <footer className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-8 text-sm text-gray-500 sm:flex-row sm:items-center sm:justify-between lg:px-8">

        <div>
          <p className="font-medium text-gray-800">
            AI Interview Coach
          </p>

          <p className="mt-1">
            Practice. Learn. Improve.
          </p>
        </div>

        <div className="flex gap-5">
          <a href="#practice">Practice</a>
          <a href="#about">About</a>
          <a href="#">Privacy</a>
          <a href="#">GitHub</a>
        </div>

      </footer>

    </main>
  )
}

export default Landing