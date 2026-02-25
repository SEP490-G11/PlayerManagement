/** @odoo-module **/

const { useEffect, useRef } = owl;

export default function useAutofocus(name) {
  let ref = useRef(name);
  useEffect(
    (el) => {
      el?.focus();
    },
    () => [ref.el]
  );
}

export function useAutofocusModal(name) {
  let ref = useRef(name);
  const modalShownEvent = "shown.bs.modal";
  useEffect(
    () => {
      const handleFocus = () => ref.el?.focus();
      $(document).on(modalShownEvent, handleFocus);

      return () => {
        $(document).off(modalShownEvent, handleFocus);
      };
    },
    () => [ref.el]
  );
}
