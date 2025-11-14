import { createHotContext as __vite__createHotContext } from '/@vite/client';
import.meta.hot = __vite__createHotContext('/src/main.jsx');
import __vite__cjsImport0_react_jsxDevRuntime from '/node_modules/.vite/deps/react_jsx-dev-runtime.js?v=b54db94a';
const jsxDEV = __vite__cjsImport0_react_jsxDevRuntime['jsxDEV'];
import __vite__cjsImport1_react from '/node_modules/.vite/deps/react.js?v=b54db94a';
const React = __vite__cjsImport1_react.__esModule
  ? __vite__cjsImport1_react.default
  : __vite__cjsImport1_react;
import __vite__cjsImport2_reactDom_client from '/node_modules/.vite/deps/react-dom_client.js?v=b54db94a';
const ReactDOM = __vite__cjsImport2_reactDom_client.__esModule
  ? __vite__cjsImport2_reactDom_client.default
  : __vite__cjsImport2_reactDom_client;
import { AuthProvider } from '/src/context/AuthContext.jsx';
import Login from '/src/pages/Login.jsx?t=1762499452854';
import SignUp from '/src/pages/SignUp.jsx';
import {
  BrowserRouter,
  Router,
  Routes,
  Route,
} from '/node_modules/.vite/deps/react-router-dom.js?v=b54db94a';
import Home from '/src/pages/Home.jsx?t=1762499452854';
import LandingPage from '/src/pages/LandingPage.jsx?t=1762499452854';
function App() {
  return /* @__PURE__ */ jsxDEV(
    'div',
    {
      children: /* @__PURE__ */ jsxDEV(
        AuthProvider,
        {
          children: /* @__PURE__ */ jsxDEV(
            BrowserRouter,
            {
              children: /* @__PURE__ */ jsxDEV(
                Routes,
                {
                  children: [
                    /* @__PURE__ */ jsxDEV(
                      Route,
                      {
                        path: '/',
                        element: /* @__PURE__ */ jsxDEV(
                          LandingPage,
                          {},
                          void 0,
                          false,
                          {
                            fileName: 'C:/Users/Admin/workspace/phongnv37/frontend/src/main.jsx',
                            lineNumber: 16,
                            columnNumber: 38,
                          },
                          this
                        ),
                      },
                      void 0,
                      false,
                      {
                        fileName: 'C:/Users/Admin/workspace/phongnv37/frontend/src/main.jsx',
                        lineNumber: 16,
                        columnNumber: 13,
                      },
                      this
                    ),
                    /* @__PURE__ */ jsxDEV(
                      Route,
                      {
                        path: '/log_in',
                        element: /* @__PURE__ */ jsxDEV(
                          Login,
                          {},
                          void 0,
                          false,
                          {
                            fileName: 'C:/Users/Admin/workspace/phongnv37/frontend/src/main.jsx',
                            lineNumber: 17,
                            columnNumber: 44,
                          },
                          this
                        ),
                      },
                      void 0,
                      false,
                      {
                        fileName: 'C:/Users/Admin/workspace/phongnv37/frontend/src/main.jsx',
                        lineNumber: 17,
                        columnNumber: 13,
                      },
                      this
                    ),
                    /* @__PURE__ */ jsxDEV(
                      Route,
                      {
                        path: '/sign-up',
                        element: /* @__PURE__ */ jsxDEV(
                          SignUp,
                          {},
                          void 0,
                          false,
                          {
                            fileName: 'C:/Users/Admin/workspace/phongnv37/frontend/src/main.jsx',
                            lineNumber: 18,
                            columnNumber: 45,
                          },
                          this
                        ),
                      },
                      void 0,
                      false,
                      {
                        fileName: 'C:/Users/Admin/workspace/phongnv37/frontend/src/main.jsx',
                        lineNumber: 18,
                        columnNumber: 13,
                      },
                      this
                    ),
                    /* @__PURE__ */ jsxDEV(
                      Route,
                      {
                        path: '/home',
                        element: /* @__PURE__ */ jsxDEV(
                          Home,
                          {},
                          void 0,
                          false,
                          {
                            fileName: 'C:/Users/Admin/workspace/phongnv37/frontend/src/main.jsx',
                            lineNumber: 19,
                            columnNumber: 42,
                          },
                          this
                        ),
                      },
                      void 0,
                      false,
                      {
                        fileName: 'C:/Users/Admin/workspace/phongnv37/frontend/src/main.jsx',
                        lineNumber: 19,
                        columnNumber: 13,
                      },
                      this
                    ),
                  ],
                },
                void 0,
                true,
                {
                  fileName: 'C:/Users/Admin/workspace/phongnv37/frontend/src/main.jsx',
                  lineNumber: 15,
                  columnNumber: 11,
                },
                this
              ),
            },
            void 0,
            false,
            {
              fileName: 'C:/Users/Admin/workspace/phongnv37/frontend/src/main.jsx',
              lineNumber: 14,
              columnNumber: 9,
            },
            this
          ),
        },
        void 0,
        false,
        {
          fileName: 'C:/Users/Admin/workspace/phongnv37/frontend/src/main.jsx',
          lineNumber: 13,
          columnNumber: 7,
        },
        this
      ),
    },
    void 0,
    false,
    {
      fileName: 'C:/Users/Admin/workspace/phongnv37/frontend/src/main.jsx',
      lineNumber: 12,
      columnNumber: 5,
    },
    this
  );
}
_c = App;
ReactDOM.createRoot(document.getElementById('root')).render(
  /* @__PURE__ */ jsxDEV(
    React.StrictMode,
    {
      children: /* @__PURE__ */ jsxDEV(
        App,
        {},
        void 0,
        false,
        {
          fileName: 'C:/Users/Admin/workspace/phongnv37/frontend/src/main.jsx',
          lineNumber: 29,
          columnNumber: 5,
        },
        this
      ),
    },
    void 0,
    false,
    {
      fileName: 'C:/Users/Admin/workspace/phongnv37/frontend/src/main.jsx',
      lineNumber: 28,
      columnNumber: 3,
    },
    this
  )
);
var _c;
$RefreshReg$(_c, 'App');
import * as RefreshRuntime from '/@react-refresh';
const inWebWorker = typeof WorkerGlobalScope !== 'undefined' && self instanceof WorkerGlobalScope;
if (import.meta.hot && !inWebWorker) {
  if (!window.$RefreshReg$) {
    throw new Error("@vitejs/plugin-react can't detect preamble. Something is wrong.");
  }
  RefreshRuntime.__hmr_import(import.meta.url).then((currentExports) => {
    RefreshRuntime.registerExportsForReactRefresh(
      'C:/Users/Admin/workspace/phongnv37/frontend/src/main.jsx',
      currentExports
    );
    import.meta.hot.accept((nextExports) => {
      if (!nextExports) return;
      const invalidateMessage = RefreshRuntime.validateRefreshBoundaryAndEnqueueUpdate(
        'C:/Users/Admin/workspace/phongnv37/frontend/src/main.jsx',
        currentExports,
        nextExports
      );
      if (invalidateMessage) import.meta.hot.invalidate(invalidateMessage);
    });
  });
}
function $RefreshReg$(type, id) {
  return RefreshRuntime.register(
    type,
    'C:/Users/Admin/workspace/phongnv37/frontend/src/main.jsx ' + id
  );
}
function $RefreshSig$() {
  return RefreshRuntime.createSignatureFunctionForTransform();
}

//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJtYXBwaW5ncyI6IkFBZXFDO0FBZnJDLE9BQU9BLFdBQVc7QUFDbEIsT0FBT0MsY0FBYztBQUNyQixTQUFTQyxvQkFBb0I7QUFDN0IsT0FBT0MsV0FBVztBQUNsQixPQUFPQyxZQUFZO0FBQ25CLFNBQVNDLGVBQWVDLFFBQVFDLFFBQVFDLGFBQWE7QUFDckQsT0FBT0MsVUFBVTtBQUNqQixPQUFPQyxpQkFBaUI7QUFFeEIsU0FBU0MsTUFBSztBQUNaLFNBQ0UsdUJBQUMsU0FDQyxpQ0FBQyxnQkFDQyxpQ0FBQyxpQkFDQyxpQ0FBQyxVQUNDO0FBQUEsMkJBQUMsU0FBTSxNQUFLLEtBQUksU0FBUyx1QkFBQyxpQkFBRDtBQUFBO0FBQUE7QUFBQTtBQUFBLFdBQVksS0FBckM7QUFBQTtBQUFBO0FBQUE7QUFBQSxXQUF5QztBQUFBLElBQ3pDLHVCQUFDLFNBQU0sTUFBSyxXQUFVLFNBQVMsdUJBQUMsV0FBRDtBQUFBO0FBQUE7QUFBQTtBQUFBLFdBQU0sS0FBckM7QUFBQTtBQUFBO0FBQUE7QUFBQSxXQUF5QztBQUFBLElBQ3pDLHVCQUFDLFNBQU0sTUFBSyxZQUFXLFNBQVMsdUJBQUMsWUFBRDtBQUFBO0FBQUE7QUFBQTtBQUFBLFdBQU8sS0FBdkM7QUFBQTtBQUFBO0FBQUE7QUFBQSxXQUEwQztBQUFBLElBQzFDLHVCQUFDLFNBQU0sTUFBSyxTQUFRLFNBQVMsdUJBQUMsVUFBRDtBQUFBO0FBQUE7QUFBQTtBQUFBLFdBQUssS0FBbEM7QUFBQTtBQUFBO0FBQUE7QUFBQSxXQUFxQztBQUFBLE9BSnZDO0FBQUE7QUFBQTtBQUFBO0FBQUEsU0FLQSxLQU5GO0FBQUE7QUFBQTtBQUFBO0FBQUEsU0FPQSxLQVJGO0FBQUE7QUFBQTtBQUFBO0FBQUEsU0FTQSxLQVZGO0FBQUE7QUFBQTtBQUFBO0FBQUEsU0FXQTtBQUVKO0FBQUNDLEtBZlFEO0FBaUJUVixTQUFTWSxXQUFXQyxTQUFTQyxlQUFlLE1BQU0sQ0FBQyxFQUFFQztBQUFBQSxFQUNuRCx1QkFBQyxNQUFNLFlBQU4sRUFDQyxpQ0FBQyxTQUFEO0FBQUE7QUFBQTtBQUFBO0FBQUEsU0FBSSxLQUROO0FBQUE7QUFBQTtBQUFBO0FBQUEsU0FFQTtBQUNGO0FBQUMsSUFBQUo7QUFBQUssYUFBQUwsSUFBQSIsIm5hbWVzIjpbIlJlYWN0IiwiUmVhY3RET00iLCJBdXRoUHJvdmlkZXIiLCJMb2dpbiIsIlNpZ25VcCIsIkJyb3dzZXJSb3V0ZXIiLCJSb3V0ZXIiLCJSb3V0ZXMiLCJSb3V0ZSIsIkhvbWUiLCJMYW5kaW5nUGFnZSIsIkFwcCIsIl9jIiwiY3JlYXRlUm9vdCIsImRvY3VtZW50IiwiZ2V0RWxlbWVudEJ5SWQiLCJyZW5kZXIiLCIkUmVmcmVzaFJlZyQiXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZXMiOlsibWFpbi5qc3giXSwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0IFJlYWN0IGZyb20gJ3JlYWN0J1xuaW1wb3J0IFJlYWN0RE9NIGZyb20gJ3JlYWN0LWRvbS9jbGllbnQnXG5pbXBvcnQgeyBBdXRoUHJvdmlkZXIgfSBmcm9tIFwiLi9jb250ZXh0L0F1dGhDb250ZXh0XCI7XG5pbXBvcnQgTG9naW4gZnJvbSBcIi4vcGFnZXMvTG9naW5cIjtcbmltcG9ydCBTaWduVXAgZnJvbSBcIi4vcGFnZXMvU2lnblVwXCI7XG5pbXBvcnQgeyBCcm93c2VyUm91dGVyLCBSb3V0ZXIsIFJvdXRlcywgUm91dGUgfSBmcm9tICdyZWFjdC1yb3V0ZXItZG9tJztcbmltcG9ydCBIb21lIGZyb20gJy4vcGFnZXMvSG9tZSc7XG5pbXBvcnQgTGFuZGluZ1BhZ2UgZnJvbSAnQHBhZ2VzL0xhbmRpbmdQYWdlJ1xuXG5mdW5jdGlvbiBBcHAoKXtcbiAgcmV0dXJuIChcbiAgICA8ZGl2PlxuICAgICAgPEF1dGhQcm92aWRlcj5cbiAgICAgICAgPEJyb3dzZXJSb3V0ZXI+XG4gICAgICAgICAgPFJvdXRlcz5cbiAgICAgICAgICAgIDxSb3V0ZSBwYXRoPVwiL1wiIGVsZW1lbnQ9ezxMYW5kaW5nUGFnZSAvPn0gLz5cbiAgICAgICAgICAgIDxSb3V0ZSBwYXRoPVwiL2xvZ19pblwiIGVsZW1lbnQ9ezxMb2dpbiAvPn0gLz5cbiAgICAgICAgICAgIDxSb3V0ZSBwYXRoPVwiL3NpZ24tdXBcIiBlbGVtZW50PXs8U2lnblVwLz59IC8+XG4gICAgICAgICAgICA8Um91dGUgcGF0aD1cIi9ob21lXCIgZWxlbWVudD17PEhvbWUvPn0gLz5cbiAgICAgICAgICA8L1JvdXRlcz5cbiAgICAgICAgPC9Ccm93c2VyUm91dGVyPlxuICAgICAgPC9BdXRoUHJvdmlkZXI+XG4gICAgPC9kaXY+XG4gIClcbn1cblxuUmVhY3RET00uY3JlYXRlUm9vdChkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgncm9vdCcpKS5yZW5kZXIoXG4gIDxSZWFjdC5TdHJpY3RNb2RlPlxuICAgIDxBcHAgLz5cbiAgPC9SZWFjdC5TdHJpY3RNb2RlPlxuKSJdLCJmaWxlIjoiQzovVXNlcnMvQWRtaW4vd29ya3NwYWNlL3Bob25nbnYzNy9mcm9udGVuZC9zcmMvbWFpbi5qc3gifQ==
