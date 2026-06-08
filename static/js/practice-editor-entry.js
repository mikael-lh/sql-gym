import { basicSetup } from "codemirror";
import { sql } from "@codemirror/lang-sql";
import { EditorView } from "@codemirror/view";

function initPracticeEditor(hostId, hiddenInputId, initialSql) {
  const host = document.getElementById(hostId);
  const hiddenInput = document.getElementById(hiddenInputId);
  if (
    !host ||
    !(
      hiddenInput instanceof HTMLTextAreaElement || hiddenInput instanceof HTMLInputElement
    )
  ) {
    return;
  }

  const syncHiddenInput = (view) => {
    hiddenInput.value = view.state.doc.toString();
  };

  const view = new EditorView({
    doc: initialSql,
    extensions: [
      basicSetup,
      sql(),
      EditorView.updateListener.of((update) => {
        if (update.docChanged) {
          syncHiddenInput(view);
        }
      }),
    ],
    parent: host,
  });

  syncHiddenInput(view);
}

globalThis.initPracticeEditor = initPracticeEditor;
