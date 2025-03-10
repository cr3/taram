import { useTranslation } from "react-i18next";
import Navbar from "../components/Navbar";

export default function NotFound() {
  const { t } = useTranslation();

  return (
    <>
      <Navbar />
      <p>{t("notFound")}</p>
    </>
  );
}
