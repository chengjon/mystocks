import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import * as ts from 'typescript'
import { HOME_ROUTE_NAME, HOME_ROUTE_PATH, LEGACY_HOME_ROUTE_PATH } from '@/router/homeRoute'

const routerSource = readFileSync(resolve(process.cwd(), 'src/router/index.ts'), 'utf8')
const comprehensiveE2ESource = readFileSync(resolve(process.cwd(), 'tests/e2e/comprehensive-all-pages.spec.ts'), 'utf8')
const routerSourceFile = ts.createSourceFile('index.ts', routerSource, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS)
const comprehensiveE2ESourceFile = ts.createSourceFile(
  'comprehensive-all-pages.spec.ts',
  comprehensiveE2ESource,
  ts.ScriptTarget.Latest,
  true,
  ts.ScriptKind.TS,
)

const identifierPathMap: Record<string, string> = {
  HOME_ROUTE_PATH,
  LEGACY_HOME_ROUTE_PATH,
}

const identifierNameMap: Record<string, string> = {
  HOME_ROUTE_NAME,
}

type RouteEntry = {
  name: string
  fullPath: string
  apiPath: string | null
}

type E2EPageEntry = {
  name: string
  path: string
  requiresAuth: boolean
  expectedSelectors: string[]
  expectedApiPath: string | null
  noApiAssertionReason: string | null
}

function readRouteString(node: ts.Expression | undefined): string | null {
  if (!node) {
    return null
  }

  if (ts.isStringLiteral(node) || ts.isNoSubstitutionTemplateLiteral(node)) {
    return node.text
  }

  if (ts.isIdentifier(node)) {
    return identifierPathMap[node.text] ?? identifierNameMap[node.text] ?? null
  }

  return null
}

function getObjectProperty(
  node: ts.ObjectLiteralExpression,
  propertyName: string,
): ts.PropertyAssignment | undefined {
  return node.properties.find(
    (property): property is ts.PropertyAssignment =>
      ts.isPropertyAssignment(property)
      && ts.isIdentifier(property.name)
      && property.name.text === propertyName,
  )
}

function joinRoutePath(parentPath: string, ownPath: string): string {
  if (ownPath.startsWith('/')) {
    return ownPath
  }

  if (!parentPath || parentPath === '/') {
    return `/${ownPath}`.replace(/\/+/g, '/')
  }

  return `${parentPath.replace(/\/$/, '')}/${ownPath}`.replace(/\/+/g, '/')
}

function collectNamedRoutes(elements: readonly ts.Expression[], parentPath = ''): RouteEntry[] {
  const routes: RouteEntry[] = []

  for (const element of elements) {
    if (!ts.isObjectLiteralExpression(element)) {
      continue
    }

    const pathProperty = getObjectProperty(element, 'path')
    const ownPath = readRouteString(pathProperty?.initializer)
    const fullPath = ownPath ? joinRoutePath(parentPath, ownPath) : parentPath

    const nameProperty = getObjectProperty(element, 'name')
    const routeName = readRouteString(nameProperty?.initializer)
    const metaProperty = getObjectProperty(element, 'meta')
    const metaObject = metaProperty?.initializer && ts.isObjectLiteralExpression(metaProperty.initializer)
      ? metaProperty.initializer
      : null
    const apiProperty = metaObject ? getObjectProperty(metaObject, 'api') : undefined
    const apiPath = readRouteString(apiProperty?.initializer)
    if (routeName && ownPath) {
      routes.push({ name: routeName, fullPath, apiPath })
    }

    const childrenProperty = getObjectProperty(element, 'children')
    if (childrenProperty && ts.isArrayLiteralExpression(childrenProperty.initializer)) {
      routes.push(...collectNamedRoutes(childrenProperty.initializer.elements, fullPath))
    }
  }

  return routes
}

function getNamedRoutesFromRouterSource(): RouteEntry[] {
  for (const statement of routerSourceFile.statements) {
    if (!ts.isVariableStatement(statement)) {
      continue
    }

    for (const declaration of statement.declarationList.declarations) {
      if (
        ts.isIdentifier(declaration.name)
        && declaration.name.text === 'routes'
        && declaration.initializer
        && ts.isArrayLiteralExpression(declaration.initializer)
      ) {
        return collectNamedRoutes(declaration.initializer.elements)
      }
    }
  }

  return []
}

function getComprehensiveE2EPagePaths(): string[] {
  return getComprehensiveE2EPageEntries().map((entry) => entry.path)
}

function readBoolean(node: ts.Expression | undefined): boolean | null {
  if (!node) {
    return null
  }

  if (node.kind === ts.SyntaxKind.TrueKeyword) {
    return true
  }

  if (node.kind === ts.SyntaxKind.FalseKeyword) {
    return false
  }

  return null
}

function readStringArray(node: ts.Expression | undefined): string[] {
  if (!node || !ts.isArrayLiteralExpression(node)) {
    return []
  }

  return node.elements
    .map((element) => readRouteString(element))
    .filter((value): value is string => Boolean(value))
}

function getComprehensiveE2EPageEntries(): E2EPageEntry[] {
  for (const statement of comprehensiveE2ESourceFile.statements) {
    if (!ts.isVariableStatement(statement)) {
      continue
    }

    for (const declaration of statement.declarationList.declarations) {
      if (
        ts.isIdentifier(declaration.name)
        && declaration.name.text === 'PAGES'
        && declaration.initializer
        && ts.isArrayLiteralExpression(declaration.initializer)
      ) {
        return declaration.initializer.elements
          .filter(ts.isObjectLiteralExpression)
          .map((element) => ({
            name: readRouteString(getObjectProperty(element, 'name')?.initializer) ?? '',
            path: readRouteString(getObjectProperty(element, 'path')?.initializer) ?? '',
            requiresAuth: readBoolean(getObjectProperty(element, 'requiresAuth')?.initializer) ?? false,
            expectedSelectors: readStringArray(getObjectProperty(element, 'expectedSelectors')?.initializer),
            expectedApiPath: readRouteString(getObjectProperty(element, 'expectedApiPath')?.initializer),
            noApiAssertionReason: readRouteString(getObjectProperty(element, 'noApiAssertionReason')?.initializer),
          }))
      }
    }
  }

  return []
}

function getCanonicalBusinessRoutes(): RouteEntry[] {
  return getNamedRoutesFromRouterSource().filter((route) =>
    route.name === 'login'
    || route.name === HOME_ROUTE_NAME
    || /^(ai|market|data|watchlist|strategy|trade|risk|system)-/.test(route.name),
  )
}

describe('comprehensive E2E route coverage', () => {
  it('covers every canonical active business route from router truth', () => {
    const routerPaths = getCanonicalBusinessRoutes().map((route) => route.fullPath).sort()
    const e2ePaths = getComprehensiveE2EPagePaths().sort()

    expect(e2ePaths).toEqual(routerPaths)
  })

  it('keeps the comprehensive E2E page inventory at 40 routed pages', () => {
    const e2ePaths = getComprehensiveE2EPagePaths()

    // The historical 35/35 figure included the backend health probe test.
    // After trade execution, trade reconciliation, and the AI sentiment/ML/batch routes, the routed page inventory is 40 entries:
    // login + 39 authenticated routes.
    expect(e2ePaths).toHaveLength(40)
  })

  it('requires every page entry to declare core visible selectors', () => {
    const pageEntries = getComprehensiveE2EPageEntries()

    for (const entry of pageEntries) {
      expect(entry.expectedSelectors.length, `${entry.name} should declare expectedSelectors`).toBeGreaterThan(0)
    }
  })

  it('requires every authenticated route entry to declare an API contract or explicit shell-only reason', () => {
    const pageEntries = getComprehensiveE2EPageEntries().filter((entry) => entry.requiresAuth)
    const routerApiByPath = new Map(
      getCanonicalBusinessRoutes()
        .filter((route) => route.fullPath !== '/login')
        .map((route) => [route.fullPath, route.apiPath]),
    )

    for (const entry of pageEntries) {
      const routerApiPath = routerApiByPath.get(entry.path) ?? null

      if (routerApiPath) {
        expect(entry.expectedApiPath, `${entry.name} should declare expectedApiPath`).toBe(routerApiPath)
        expect(entry.noApiAssertionReason, `${entry.name} should not declare a shell-only reason`).toBeNull()
      } else {
        expect(entry.expectedApiPath, `${entry.name} should omit expectedApiPath for shell-only routes`).toBeNull()
        expect(
          (entry.noApiAssertionReason ?? '').length,
          `${entry.name} should declare noApiAssertionReason`,
        ).toBeGreaterThan(0)
      }
    }
  })
})
