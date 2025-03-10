import { useTranslation } from "react-i18next";
import Navbar from "../components/Navbar";

export default function Home() {
  const { t } = useTranslation();

  return (
    <>
      <Navbar />
      <p>{t("construction")}</p>
    </>
  );
}
