import { useTranslation } from "react-i18next";
import Lang from "./Lang";

export default function Navbar() {
  const { t } = useTranslation();

  return (
    <nav className="flex flex-wrap items-center justify-between bg-teal-500 p-6">
      <div className="mr-6 flex flex-shrink-0 items-center text-white">
        <span className="font-semibold text-xl tracking-tight">Taram</span>
      </div>
      <div className="block lg:hidden">
        <button
          className="flex items-center rounded border border-teal-400 px-3 py-2 text-teal-200 hover:border-white hover:text-white"
          type="button"
        >
          <svg
            className="h-3 w-3 fill-current"
            viewBox="0 0 20 20"
            xmlns="http://www.w3.org/2000/svg"
          >
            <title>Menu</title>
            <path d="M0 3h20v2H0V3zm0 6h20v2H0V9zm0 6h20v2H0v-2z" />
          </svg>
        </button>
      </div>
      <div className="block w-full flex-grow lg:flex lg:w-auto lg:items-center">
        <div className="text-sm lg:flex-grow">
          <a
            href="/monit"
            className="mt-4 mr-4 block text-teal-200 hover:text-white lg:mt-0 lg:inline-block"
          >
            {t("monit")}
          </a>
        </div>
        <div>
          <Lang />
        </div>
      </div>
    </nav>
  );
}
