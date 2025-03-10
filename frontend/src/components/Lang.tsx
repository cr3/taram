import { useState } from "react";
import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";

interface Language {
  code: string;
  label: string;
}

export const LANGUAGES: Language[] = [
  { code: "en", label: "English" },
  { code: "fr", label: "Français" },
];

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: "fr",
    supportedLngs: LANGUAGES.map((l) => l.code),
    interpolation: {
      escapeValue: false,
    },
    resources: {
      en: {
        translation: {
          aboutLabel: "About",
          construction: "Under construction",
          emailLabel: "Email",
          monit: "Monitoring",
          notFound: "Page not found",
          title: "Taram Community",
        },
      },
      fr: {
        translation: {
          aboutLabel: "À propos",
          construction: "En construction",
          emailLabel: "Courriel",
          monit: "Monitoring",
          notFound: "Page non trouvée",
          title: "Communauté de Taram",
        },
      },
    },
  });

const nextLanguage = () => {
  const code = i18n.resolvedLanguage;
  const currentIndex = LANGUAGES.findIndex((l) => l.code === code);
  const nextIndex = (currentIndex + 1) % LANGUAGES.length;
  return LANGUAGES[nextIndex];
};

export default function Lang() {
  const [lang, setLang] = useState(nextLanguage());

  const toggleLang = () => {
    i18n.changeLanguage(lang.code);
    setLang(nextLanguage());
  };

  return (
    <button
      className="mt-4 inline-block rounded border border-white px-4 py-2 text-sm text-white leading-none hover:border-transparent hover:bg-white hover:text-teal-500 lg:mt-0"
      onClick={toggleLang}
      type="button"
    >
      {lang.label}
    </button>
  );
}
