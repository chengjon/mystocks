import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import * as ts from 'typescript'
import { HOME_ROUTE_NAME, HOME_ROUTE_PATH, LEGACY_HOME_ROUTE_PATH } from '@/router/homeRoute'

const routerSource = readFileSync(resolve(process.cwd(), 'src/router/index.ts'), 'utf8')
const comprehensiveE2ESource = readFileSync(resolve(process.cwd(), 'tests/e2e/comprehensive-all-pages.spec.ts'), 'utf8')
const routerSourceFile = ts.createSourceFile('index.ts', routerSource, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS)

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
    if (routeName && ownPath) {
      routes.push({ name: routeName, fullPath })
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
  const pageEntryPattern = /\{\s*name:\s*'[^']+',\s*path:\s*'([^']+)'/g
  const paths: string[] = []

  for (const match of comprehensiveE2ESource.matchAll(pageEntryPattern)) {
    const [, path] = match
    if (path) {
      paths.push(path)
    }
  }

  return paths
}

function getCanonicalBusinessRoutes(): RouteEntry[] {
  return getNamedRoutesFromRouterSource().filter((route) =>
    route.name === 'login'
    || route.name === HOME_ROUTE_NAME
    || /^(market|data|watchlist|strategy|trade|risk|system)-/.test(route.name),
  )
}

describe('comprehensive E2E route coverage', () => {
  it('covers every canonical active business route from router truth', () => {
    const routerPaths = getCanonicalBusinessRoutes().map((route) => route.fullPath).sort()
    const e2ePaths = getComprehensiveE2EPagePaths().sort()

    expect(e2ePaths).toEqual(routerPaths)
  })

  it('keeps the comprehensive E2E page inventory at 34 routed pages', () => {
    const e2ePaths = getComprehensiveE2EPagePaths()

    // The historical 35/35 figure includes the backend health probe test.
    // The routed page inventory itself is 34 entries: login + 33 authenticated routes.
    expect(e2ePaths).toHaveLength(34)
  })
})
