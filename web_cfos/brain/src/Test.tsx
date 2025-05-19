import {
  flexRender,
  getCoreRowModel,
  ColumnDef,
  useReactTable,
  Column,
} from "@tanstack/react-table";
import { ColumnFiltersState, getFilteredRowModel, getPaginationRowModel, RowSelectionState, SortingState, getSortedRowModel, ColumnResizeMode, ColumnResizeDirection } from "@tanstack/react-table";
import { useState, useEffect, useMemo, useRef, HTMLProps } from 'react'


export type Show = {
  color: string;
  ["TG number"]: string;
  ["Region ID"]: string;
  ["Region Name"]: string;
  fold: number;
};
/*
export type Show = {
  show: {
    status: string;
    name: string;
    type: string;
    language: string;
    genres: string[];
    runtime: number;
  };
};
*/
// now create types for props for this Table component(https://tanstack.com/table/latest/docs/framework/react/examples/sub-components)
type TableProps<TData> = {
  data: TData[];
  columns: ColumnDef<TData>[];
};


function Table({ columns, data,setSelectedRows }: TableProps<Show>) {
  //use the useReact table Hook to build our table:
const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
const [sorting, setSorting] = useState<SortingState>([]);
const [columnResizeMode, setColumnResizeMode] = useState<ColumnResizeMode>("onChange");

const [columnResizeDirection, setColumnResizeDirection] = useState<ColumnResizeDirection>("ltr");
const [rowSelection, setRowSelection] = useState<RowSelectionState>({}) //manage your own row selection state

const table = useReactTable({
    //pass in our data
    data,
    columns,
    columnResizeMode, //specify that we'll use resizing in this table
    columnResizeDirection,
    debugTable: true,
    debugHeaders: true,
    debugColumns: true,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(), //row model to filter the table
    getSortedRowModel: getSortedRowModel(),
    onSortingChange: setSorting,
    //onRowSelectionChange: setRowSelection, //hoist up the row selection state to your own scope
    enableRowSelection: true,
    enableMultiRowSelection: false,
    getPaginationRowModel: getPaginationRowModel(),
    state: {
      rowSelection,
      columnFilters,
      sorting
    },
    onColumnFiltersChange: setColumnFilters,
    onRowSelectionChange: (newSelection) => {
      //console.log('333')
      //console.log(newSelection)
      setSelectedRows(newSelection);
      setRowSelection(newSelection)
    },
  });
  
  // Table component logic and UI come here
  return (
    <div style={{ direction: table.options.columnResizeDirection }}>
      <table {...{
        style: {
          width: table.getCenterTotalSize(),
        },
      }}>
        <thead>
          {/*use the getHeaderGRoup function to render headers:*/}
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th   {...{
                  key: header.id,
                  colSpan: header.colSpan,
                  style: {
                    width: header.getSize(),
                  },
                }}>
                  {header.isPlaceholder ? null : (
                    <div
                      //when clicked, check if it can be sorted
                      //if it can, then sort this column
                      onClick={header.column.getToggleSortingHandler()}
                      title={
                        header.column.getCanSort()
                          ? header.column.getNextSortingOrder() === "asc"
                            ? "Sort ascending"
                            : header.column.getNextSortingOrder() === "desc"
                              ? "Sort descending"
                              : "Clear sort"
                          : undefined
                      }
                    >
                      {flexRender(
                        header.column.columnDef.header,
                        header.getContext(),
                      )}

                      <div
                        {...{
                          onDoubleClick: () => header.column.resetSize(),
                          //when held down, enable resizing functionality.
                          onMouseDown: header.getResizeHandler(),
                          onTouchStart: header.getResizeHandler(),
                          className: `resizer ${table.options.columnResizeDirection
                            } ${header.column.getIsResizing() ? "isResizing" : ""}`,
                          style: {
                            //keep on increasing/decreasing the column till resize mode is finished.
                            transform:
                              columnResizeMode === "onEnd" &&
                                header.column.getIsResizing()
                                ? `translateX(${(table.options.columnResizeDirection === "rtl"
                                  ? -1
                                  : 1) *
                                (table.getState().columnSizingInfo.deltaOffset ??
                                  0)
                                }px)`
                                : "",
                          },
                        }}
                      />
                      {{
                        //display a relevant icon for sorting order:
                        asc: " 🔼",
                        desc: " 🔽",
                      }[header.column.getIsSorted() as string] ?? null}



                    </div>



                  )
                  }



                  <div>
                    {/*If the column can be filtered, render the Filter component.*/}
                    {header.column.getCanFilter() ? (
                      <div>
                        <Filter column={header.column} />
                      </div>
                    ) : null}
                  </div>

                  <div
                    {...{
                      onDoubleClick: () => header.column.resetSize(),
                      //when held down, enable resizing functionality.
                      onMouseDown: header.getResizeHandler(),
                      onTouchStart: header.getResizeHandler(),
                      className: `resizer ${table.options.columnResizeDirection
                        } ${header.column.getIsResizing() ? "isResizing" : ""}`,
                      style: {
                        //keep on increasing/decreasing the column till resize mode is finished.
                        transform:
                          columnResizeMode === "onEnd" &&
                            header.column.getIsResizing()
                            ? `translateX(${(table.options.columnResizeDirection === "rtl"
                              ? -1
                              : 1) *
                            (table.getState().columnSizingInfo.deltaOffset ??
                              0)
                            }px)`
                            : "",
                      },
                    }}
                  />

                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {/*Now render the cells*/}
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id}
              className={row.getIsSelected() ? 'row_selected' : ''}
              onClick={row.getToggleSelectedHandler()}
              
            >
              {row.getVisibleCells().map((cell) => (
                <td  {...{
                  key: cell.id,
                  style: {
                    //set the width of this column
                    width: cell.column.getSize(),

                  },
                }}>
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <td className="p-1">
              <IndeterminateCheckbox
                {...{
                  checked: table.getIsAllPageRowsSelected(),
                  indeterminate: table.getIsSomePageRowsSelected(),
                  onChange: table.getToggleAllPageRowsSelectedHandler(),
                }}
              />
            </td>
            <td colSpan={20}>Page Rows ({table.getRowModel().rows.length})</td>
          </tr>
        </tfoot>
      </table>

      <div className="h-2" />
      <div className="flex items-center gap-2">
        <button
          className="border rounded p-1"
          onClick={() => table.setPageIndex(0)}
          disabled={!table.getCanPreviousPage()}
        >
          {'<<'}
        </button>
        <button
          className="border rounded p-1"
          onClick={() => table.previousPage()}
          disabled={!table.getCanPreviousPage()}
        >
          {'<'}
        </button>
        <button
          className="border rounded p-1"
          onClick={() => table.nextPage()}
          disabled={!table.getCanNextPage()}
        >
          {'>'}
        </button>
        <button
          className="border rounded p-1"
          onClick={() => table.setPageIndex(table.getPageCount() - 1)}
          disabled={!table.getCanNextPage()}
        >
          {'>>'}
        </button>
        <span className="flex items-center gap-1">
          <div>Page</div>
          <strong>
            {table.getState().pagination.pageIndex + 1} of{' '}
            {table.getPageCount()}
          </strong>
        </span>

        <select
          value={table.getState().pagination.pageSize}
          onChange={e => {
            table.setPageSize(Number(e.target.value))
          }}
        >
          {[10, 20, 30, 40, 50].map(pageSize => (
            <option key={pageSize} value={pageSize}>
              Show {pageSize}
            </option>
          ))}
        </select>
      </div>
      <br />



    </div>


  );
}

function IndeterminateCheckbox({
  indeterminate,
  className = '',
  ...rest
}: { indeterminate?: boolean } & HTMLProps<HTMLInputElement>) {
  const ref = useRef<HTMLInputElement>(null!)

  useEffect(() => {
    if (typeof indeterminate === 'boolean') {
      ref.current.indeterminate = !rest.checked && indeterminate
    }
  }, [ref, indeterminate])

  return (
    <input
      type="checkbox"
      ref={ref}
      className={className + ' cursor-pointer'}
      {...rest}
    />
  )
}

//create a Filter component to use for column searching:
function Filter({ column }: { column: Column<Show, unknown> }) {
  const columnFilterValue = column.getFilterValue();

  return (
    <Searchbar
      onChange={(value) => {
        column.setFilterValue(value);
      }}
      placeholder={`Search...`}
      type="text"
      value={(columnFilterValue ?? "") as string}
    />
  );
}
//Create a searchbar:
function Searchbar({
  value: initialValue,
  onChange,
  ...props
}: {

  value: string | number;
  onChange: (value: string | number) => void;
} & Omit<React.InputHTMLAttributes<HTMLInputElement>, "onChange">) {
  const [value, setValue] = useState(initialValue);
  useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);
  //if the entered value changes, run the onChange handler once again.
  useEffect(() => {
    onChange(value);
  }, [value]);
  //render the basic searchbar:
  return (
    <input
      {...props}
      value={value}
      onChange={(e) => setValue(e.target.value)}
    />
  );
}
export default  Table