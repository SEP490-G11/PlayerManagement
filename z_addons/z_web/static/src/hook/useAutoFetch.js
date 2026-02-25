/** @odoo-module **/

const { useEffect } = owl;

export function useAutoFetchModal(name, handler) {
  const modalShownEvent = "shown.bs.modal";
  useEffect(
    () => {
      const modal = document.getElementById(name);
      const onHandler = () => handler();
      if (modal) {
        modal.addEventListener(modalShownEvent, onHandler);
      }

      $(document).on(modalShownEvent, () => handler());

      return () => {
        if (modal) {
          modal.removeEventListener(modalShownEvent, onHandler);
        }
      };
    },
    () => []
  );
}
